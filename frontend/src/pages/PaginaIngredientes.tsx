import { useState, useEffect, FC } from 'react';
import { ingredienteService, Ingrediente } from '../services/api';
import { useToast } from '../context/ToastContext';
import Modal from '../components/Modal';
import ConfirmModal from '../components/ConfirmModal';

const PaginaIngredientes: FC = () => {
  const [ingredientes, setIngredientes] = useState<Ingrediente[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [ingredienteToDelete, setIngredienteToDelete] = useState<Ingrediente | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [searchNombre, setSearchNombre] = useState('');
  const [formData, setFormData] = useState({ nombre: '', unidad: '' });
  const [ingredientesEnUso, setIngredientesEnUso] = useState<Set<number>>(new Set());
  
  const { showToast } = useToast();

  const cargarIngredientes = async () => {
    setLoading(true);
    try {
      const response = await ingredienteService.getAll({ 
        nombre: searchNombre || undefined,
        limit: 100
      });
      setIngredientes(response.data);
      
      // Check which ingredients are in use
      const enUso = new Set<number>();
      for (const ing of response.data) {
        try {
          const res = await ingredienteService.verificarEnUso(ing.id);
          if (res.data.en_uso) {
            enUso.add(ing.id);
          }
        } catch {
          // Ignore errors
        }
      }
      setIngredientesEnUso(enUso);
    } catch {
      showToast('error', 'Error al cargar ingredientes');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarIngredientes();
  }, [searchNombre]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const nombreTrim = formData.nombre.trim();
    const unidadTrim = formData.unidad.trim();
    
    if (!nombreTrim) {
      showToast('error', 'El nombre es requerido');
      return;
    }
    if (!unidadTrim) {
      showToast('error', 'La unidad es requerida');
      return;
    }

    try {
      if (editingId) {
        // Check if trying to edit an ingredient in use
        if (ingredientesEnUso.has(editingId)) {
          showToast('error', 'No se puede editar - esta en uso');
          return;
        }
        await ingredienteService.update(editingId, { 
          nombre: nombreTrim, 
          unidad: unidadTrim 
        });
        showToast('success', 'Ingrediente actualizado');
      } else {
        await ingredienteService.create({ 
          nombre: nombreTrim, 
          unidad: unidadTrim 
        });
        showToast('success', 'Ingrediente creado');
      }
      resetForm();
      cargarIngredientes();
    } catch (err: any) {
      showToast('error', err.response?.data?.detail || 'Error al guardar');
    }
  };

  const handleEdit = (ingrediente: Ingrediente) => {
    // Check if in use
    if (ingredientesEnUso.has(ingrediente.id)) {
      showToast('error', 'No se puede editar - esta en uso');
      return;
    }
    setFormData({ nombre: ingrediente.nombre, unidad: ingrediente.unidad || '' });
    setEditingId(ingrediente.id);
    setShowModal(true);
  };

  const handleDeleteClick = (ingrediente: Ingrediente) => {
    if (ingredientesEnUso.has(ingrediente.id)) {
      showToast('error', 'No se puede eliminar - esta en uso');
      return;
    }
    setIngredienteToDelete(ingrediente);
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = async () => {
    if (!ingredienteToDelete) return;
    try {
      await ingredienteService.delete(ingredienteToDelete.id);
      showToast('success', 'Ingrediente eliminado');
      cargarIngredientes();
    } catch {
      showToast('error', 'No se puede eliminar');
    }
    setIngredienteToDelete(null);
  };

  const resetForm = () => {
    setFormData({ nombre: '', unidad: '' });
    setEditingId(null);
    setShowModal(false);
  };

  // Filter by case-insensitive search
  const filteredIngredientes = searchNombre
    ? ingredientes.filter(i => 
        i.nombre.toLowerCase().includes(searchNombre.toLowerCase()) ||
        i.unidad.toLowerCase().includes(searchNombre.toLowerCase())
      )
    : ingredientes;

  return (
    <div className="container">
      {/* Header */}
      <div className="header-actions">
        <h2 className="header-title">Ingredientes</h2>
        
        <div className="header-toolbar">
          <input
            type="text"
            className="search-input"
            placeholder="Buscar por nombre o unidad..."
            value={searchNombre}
            onChange={(e) => setSearchNombre(e.target.value)}
          />
          <button className="btn btn-primary" onClick={() => { resetForm(); setShowModal(true); }}>
            + Nuevo
          </button>
        </div>
      </div>

      {/* Loading */}
      {loading ? (
        <div className="loading-container">
          <div className="spinner"></div>
        </div>
      ) : filteredIngredientes.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-title">
            {searchNombre ? 'No se encontraron ingredientes' : 'No hay ingredientes'}
          </div>
          <div className="empty-state-text">
            {searchNombre ? 'Intenta con otros terminos' : 'Crea tu primer ingrediente'}
          </div>
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Unidad</th>
                <th style={{ width: '160px' }}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filteredIngredientes.map((ing) => {
                const enUso = ingredientesEnUso.has(ing.id);
                return (
                  <tr key={ing.id} className={enUso ? 'row-disabled' : ''}>
                    <td className="font-medium">
                      {ing.nombre}
                      {enUso && <span className="badge badge-warning ms-sm">En uso</span>}
                    </td>
                    <td>
                      <span className="badge badge-secondary">{ing.unidad}</span>
                    </td>
                    <td>
                      <div className="actions-bar">
                        <button 
                          className="btn btn-ghost btn-sm" 
                          onClick={() => handleEdit(ing)}
                          disabled={enUso}
                        >
                          {enUso ? 'Bloqueado' : 'Editar'}
                        </button>
                        <button 
                          className="btn btn-ghost btn-sm text-error" 
                          onClick={() => handleDeleteClick(ing)}
                          disabled={enUso}
                        >
                          {enUso ? 'Bloqueado' : 'Eliminar'}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal Create/Edit */}
      <Modal
        isOpen={showModal}
        onClose={resetForm}
        title={editingId ? 'Editar Ingrediente' : 'Nuevo Ingrediente'}
        footer={
          <>
            <button className="btn btn-secondary" onClick={resetForm}>Cancelar</button>
            <button className="btn btn-success" onClick={handleSubmit}>
              {editingId ? 'Actualizar' : 'Crear'}
            </button>
          </>
        }
      >
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Nombre *</label>
            <input
              type="text"
              value={formData.nombre}
              onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              maxLength={50}
              autoFocus
            />
          </div>
          <div className="form-group">
            <label>Unidad *</label>
            <input
              type="text"
              value={formData.unidad}
              onChange={(e) => setFormData({ ...formData, unidad: e.target.value })}
              maxLength={20}
              placeholder="kg, gramos, litros, unidades..."
            />
          </div>
        </form>
      </Modal>

      {/* Confirm Delete Modal */}
      <ConfirmModal
        isOpen={showDeleteModal}
        onClose={() => { setShowDeleteModal(false); setIngredienteToDelete(null); }}
        onConfirm={handleConfirmDelete}
        title="Eliminar Ingrediente"
        message={`Estas seguro de eliminar "${ingredienteToDelete?.nombre}"? Esta accion no se puede deshacer.`}
        confirmText="Eliminar"
        type="danger"
      />
    </div>
  );
};

export default PaginaIngredientes;