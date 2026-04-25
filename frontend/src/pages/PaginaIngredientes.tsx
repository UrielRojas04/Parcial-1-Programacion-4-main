import { useState, useEffect, FC } from 'react';
import { ingredienteService, Ingrediente } from '../services/api';

interface FormData {
  nombre: string;
  unidad: string;
}

interface Pagination {
  offset: number;
  limit: number;
}

const PaginaIngredientes: FC = () => {
  const [ingredientes, setIngredientes] = useState<Ingrediente[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [searchNombre, setSearchNombre] = useState('');
  const [pagination, setPagination] = useState<Pagination>({ offset: 0, limit: 10 });

  const [formData, setFormData] = useState<FormData>({
    nombre: '',
    unidad: '',
  });

  // Cargar ingredientes
  const cargarIngredientes = async (offset: number = 0) => {
    setLoading(true);
    setError('');
    try {
      const response = await ingredienteService.getAll({
        nombre: searchNombre || undefined,
        offset,
        limit: pagination.limit,
      });
      setIngredientes(response.data);
      setPagination(prev => ({ ...prev, offset }));
    } catch (err: any) {
      setError('Error al cargar ingredientes: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarIngredientes();
  }, [searchNombre]);

  // Manejar submit del formulario
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!formData.nombre.trim()) {
      setError('El nombre es requerido');
      return;
    }

    if (!formData.unidad.trim()) {
      setError('La unidad es requerida');
      return;
    }

    try {
      if (editingId) {
        await ingredienteService.update(editingId, formData);
        setSuccess('Ingrediente actualizado correctamente');
      } else {
        await ingredienteService.create(formData);
        setSuccess('Ingrediente creado correctamente');
      }
      resetForm();
      cargarIngredientes(0);
    } catch (err: any) {
      setError('Error: ' + (err.response?.data?.detail || err.message));
    }
  };

  // Editar ingrediente
  const handleEdit = (ingrediente: Ingrediente) => {
    setFormData({
      nombre: ingrediente.nombre,
      unidad: ingrediente.unidad || '',
    });
    setEditingId(ingrediente.id);
    setShowForm(true);
  };

  // Eliminar ingrediente
  const handleDelete = async (id: number) => {
    if (!confirm('¿Está seguro de que desea eliminar este ingrediente?')) return;

    try {
      await ingredienteService.delete(id);
      setSuccess('Ingrediente eliminado correctamente');
      cargarIngredientes(0);
    } catch (err: any) {
      setError('Error: ' + (err.response?.data?.detail || err.message));
    }
  };

  // Reset del formulario
  const resetForm = () => {
    setFormData({ nombre: '', unidad: '' });
    setEditingId(null);
    setShowForm(false);
  };

  return (
    <div className="container">
      <h2 className="section-title">🥘 Gestión de Ingredientes</h2>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {/* Barra de búsqueda */}
      <div className="form-group">
        <input
          type="text"
          placeholder="Buscar ingrediente por nombre..."
          value={searchNombre}
          onChange={(e) => setSearchNombre(e.target.value)}
        />
      </div>

      {/* Botón agregar */}
      <button className="btn btn-primary" onClick={() => { resetForm(); setShowForm(true); }}>
        ➕ Nuevo Ingrediente
      </button>

      {/* Formulario modal */}
      {showForm && (
        <div className="modal-overlay" onClick={resetForm}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">
                {editingId ? '✏️ Editar Ingrediente' : '➕ Nuevo Ingrediente'}
              </h3>
              <button className="modal-close" onClick={resetForm}>✕</button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Nombre *</label>
                <input
                  type="text"
                  value={formData.nombre}
                  onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                  maxLength={50}
                />
              </div>

              <div className="form-group">
                <label>Unidad (kg, l, porciones, etc.) *</label>
                <input
                  type="text"
                  value={formData.unidad}
                  onChange={(e) => setFormData({ ...formData, unidad: e.target.value })}
                  maxLength={20}
                  placeholder="Ej: kg, gramos, litros, etc."
                />
              </div>

              <div className="btn-group">
                <button type="submit" className="btn btn-success">
                  {editingId ? '💾 Actualizar' : '➕ Crear'}
                </button>
                <button type="button" className="btn btn-secondary" onClick={resetForm}>
                  ✕ Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Tabla de ingredientes */}
      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
          <p>Cargando...</p>
        </div>
      ) : (
        <>
          {ingredientes.length === 0 ? (
            <div className="alert alert-info">No hay ingredientes para mostrar</div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nombre</th>
                  <th>Unidad</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {ingredientes.map((ingrediente) => (
                  <tr key={ingrediente.id}>
                    <td>#{ingrediente.id}</td>
                    <td>{ingrediente.nombre}</td>
                    <td>{ingrediente.unidad}</td>
                    <td>
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => handleEdit(ingrediente)}
                      >
                        ✏️
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(ingrediente.id)}
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {/* Paginación */}
          <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
            <button
              className="btn btn-secondary"
              onClick={() => cargarIngredientes(Math.max(0, pagination.offset - pagination.limit))}
              disabled={pagination.offset === 0}
            >
              ← Anterior
            </button>
            <span style={{ alignSelf: 'center', color: '#666' }}>
              Página {Math.floor(pagination.offset / pagination.limit) + 1}
            </span>
            <button
              className="btn btn-secondary"
              onClick={() => cargarIngredientes(pagination.offset + pagination.limit)}
              disabled={ingredientes.length < pagination.limit}
            >
              Siguiente →
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default PaginaIngredientes;
