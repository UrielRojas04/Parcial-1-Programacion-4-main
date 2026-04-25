import { useState, useEffect, FC } from 'react';
import { categoriaService, Categoria } from '../services/api';

interface FormData {
  nombre: string;
  descripcion: string;
}

interface Pagination {
  offset: number;
  limit: number;
}

const PaginaCategorias: FC = () => {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [searchNombre, setSearchNombre] = useState('');
  const [pagination, setPagination] = useState<Pagination>({ offset: 0, limit: 10 });

  const [formData, setFormData] = useState<FormData>({
    nombre: '',
    descripcion: '',
  });

  // Cargar categorías
  const cargarCategorias = async (offset: number = 0) => {
    setLoading(true);
    setError('');
    try {
      const response = await categoriaService.getAll({
        nombre: searchNombre || undefined,
        offset,
        limit: pagination.limit,
      });
      setCategorias(response.data);
      setPagination(prev => ({ ...prev, offset }));
    } catch (err: any) {
      setError('Error al cargar categorías: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarCategorias();
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

    try {
      if (editingId) {
        await categoriaService.update(editingId, formData);
        setSuccess('Categoría actualizada correctamente');
      } else {
        await categoriaService.create(formData);
        setSuccess('Categoría creada correctamente');
      }
      resetForm();
      cargarCategorias(0);
    } catch (err: any) {
      setError('Error: ' + (err.response?.data?.detail || err.message));
    }
  };

  // Editar categoría
  const handleEdit = (categoria: Categoria) => {
    setFormData({
      nombre: categoria.nombre,
      descripcion: categoria.descripcion || '',
    });
    setEditingId(categoria.id);
    setShowForm(true);
  };

  // Eliminar categoría
  const handleDelete = async (id: number) => {
    if (!confirm('¿Está seguro de que desea eliminar esta categoría?')) return;

    try {
      await categoriaService.delete(id);
      setSuccess('Categoría eliminada correctamente');
      cargarCategorias(0);
    } catch (err: any) {
      setError('Error: ' + (err.response?.data?.detail || err.message));
    }
  };

  // Reset del formulario
  const resetForm = () => {
    setFormData({ nombre: '', descripcion: '' });
    setEditingId(null);
    setShowForm(false);
  };

  return (
    <div className="container">
      <h2 className="section-title">📂 Gestión de Categorías</h2>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {/* Barra de búsqueda */}
      <div className="form-group">
        <input
          type="text"
          placeholder="Buscar categoría por nombre..."
          value={searchNombre}
          onChange={(e) => setSearchNombre(e.target.value)}
        />
      </div>

      {/* Botón agregar */}
      <button className="btn btn-primary" onClick={() => { resetForm(); setShowForm(true); }}>
        ➕ Nueva Categoría
      </button>

      {/* Formulario modal */}
      {showForm && (
        <div className="modal-overlay" onClick={resetForm}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">
                {editingId ? '✏️ Editar Categoría' : '➕ Nueva Categoría'}
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
                <label>Descripción</label>
                <textarea
                  value={formData.descripcion}
                  onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                  maxLength={200}
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

      {/* Tabla de categorías */}
      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
          <p>Cargando...</p>
        </div>
      ) : (
        <>
          {categorias.length === 0 ? (
            <div className="alert alert-info">No hay categorías para mostrar</div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nombre</th>
                  <th>Descripción</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {categorias.map((categoria) => (
                  <tr key={categoria.id}>
                    <td>#{categoria.id}</td>
                    <td>{categoria.nombre}</td>
                    <td>{categoria.descripcion || '-'}</td>
                    <td>
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => handleEdit(categoria)}
                      >
                        ✏️
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDelete(categoria.id)}
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
              onClick={() => cargarCategorias(Math.max(0, pagination.offset - pagination.limit))}
              disabled={pagination.offset === 0}
            >
              ← Anterior
            </button>
            <span style={{ alignSelf: 'center', color: '#666' }}>
              Página {Math.floor(pagination.offset / pagination.limit) + 1}
            </span>
            <button
              className="btn btn-secondary"
              onClick={() => cargarCategorias(pagination.offset + pagination.limit)}
              disabled={categorias.length < pagination.limit}
            >
              Siguiente →
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default PaginaCategorias;
