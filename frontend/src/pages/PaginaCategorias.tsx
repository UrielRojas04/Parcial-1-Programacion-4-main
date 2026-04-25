import { useState, useEffect, FC } from 'react';
import { categoriaService, Categoria } from '../services/api';
import { useToast } from '../context/ToastContext';
import Modal from '../components/Modal';
import ConfirmModal from '../components/ConfirmModal';

const PaginaCategorias: FC = () => {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [categoriaToDelete, setCategoriaToDelete] = useState<Categoria | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [searchNombre, setSearchNombre] = useState('');
  const [formData, setFormData] = useState({ nombre: '', descripcion: '' });
  const [categoriasEnUso, setCategoriasEnUso] = useState<Set<number>>(new Set());
  
  const { showToast } = useToast();

  const cargarCategorias = async () => {
    setLoading(true);
    try {
      const response = await categoriaService.getAll({ 
        nombre: searchNombre || undefined,
        limit: 100
      });
      setCategorias(response.data);
      
      // Check which categories are in use
      const enUso = new Set<number>();
      for (const cat of response.data) {
        try {
          const res = await categoriaService.verificarEnUso(cat.id);
          if (res.data.en_uso) {
            enUso.add(cat.id);
          }
        } catch {
          // Ignore errors
        }
      }
      setCategoriasEnUso(enUso);
    } catch {
      showToast('error', 'Error al cargar categorias');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarCategorias();
  }, [searchNombre]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const nombreTrim = formData.nombre.trim();
    if (!nombreTrim) {
      showToast('error', 'El nombre es requerido');
      return;
    }

    try {
      if (editingId) {
        // Check if trying to edit a category in use
        if (categoriasEnUso.has(editingId)) {
          showToast('error', 'No se puede editar - esta en uso');
          return;
        }
        await categoriaService.update(editingId, { 
          nombre: nombreTrim, 
          descripcion: formData.descripcion 
        });
        showToast('success', 'Categoria actualizada');
      } else {
        await categoriaService.create({ 
          nombre: nombreTrim, 
          descripcion: formData.descripcion 
        });
        showToast('success', 'Categoria creada');
      }
      resetForm();
      cargarCategorias();
    } catch (err: any) {
      showToast('error', err.response?.data?.detail || 'Error al guardar');
    }
  };

  const handleEdit = (categoria: Categoria) => {
    // Check if in use
    if (categoriasEnUso.has(categoria.id)) {
      showToast('error', 'No se puede editar - esta en uso');
      return;
    }
    setFormData({ nombre: categoria.nombre, descripcion: categoria.descripcion || '' });
    setEditingId(categoria.id);
    setShowModal(true);
  };

  const handleDeleteClick = (categoria: Categoria) => {
    if (categoriasEnUso.has(categoria.id)) {
      showToast('error', 'No se puede eliminar - esta en uso');
      return;
    }
    setCategoriaToDelete(categoria);
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = async () => {
    if (!categoriaToDelete) return;
    try {
      await categoriaService.delete(categoriaToDelete.id);
      showToast('success', 'Categoria eliminada');
      cargarCategorias();
    } catch (err: any) {
      showToast('error', 'No se puede eliminar');
    }
    setCategoriaToDelete(null);
  };

  const resetForm = () => {
    setFormData({ nombre: '', descripcion: '' });
    setEditingId(null);
    setShowModal(false);
  };

  // Filter categorias client-side for case-insensitive search
  const filteredCategorias = searchNombre
    ? categorias.filter(c => 
        c.nombre.toLowerCase().includes(searchNombre.toLowerCase()) ||
        (c.descripcion && c.descripcion.toLowerCase().includes(searchNombre.toLowerCase()))
      )
    : categorias;

  return (
    <div className="container">
      {/* Header */}
      <div className="header-actions">
        <h2 className="header-title">Categorias</h2>
        
        <div className="header-toolbar">
          <input
            type="text"
            className="search-input"
            placeholder="Buscar por nombre o descripcion..."
            value={searchNombre}
            onChange={(e) => setSearchNombre(e.target.value)}
          />
          <button className="btn btn-primary" onClick={() => { resetForm(); setShowModal(true); }}>
            + Nueva
          </button>
        </div>
      </div>

      {/* Loading */}
      {loading ? (
        <div className="loading-container">
          <div className="spinner"></div>
        </div>
      ) : filteredCategorias.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-title">
            {searchNombre ? 'No se encontraron categorias' : 'No hay categorias'}
          </div>
          <div className="empty-state-text">
            {searchNombre ? 'Intenta con otros terminos' : 'Crea tu primera categoria'}
          </div>
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Descripcion</th>
                <th style={{ width: '160px' }}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filteredCategorias.map((cat) => {
                const enUso = categoriasEnUso.has(cat.id);
                return (
                  <tr key={cat.id} className={enUso ? 'row-disabled' : ''}>
                    <td className="font-medium">
                      {cat.nombre}
                      {enUso && <span className="badge badge-warning ms-sm">En uso</span>}
                    </td>
                    <td className="text-muted">{cat.descripcion || '-'}</td>
                    <td>
                      <div className="actions-bar">
                        <button 
                          className="btn btn-ghost btn-sm" 
                          onClick={() => handleEdit(cat)}
                          disabled={enUso}
                        >
                          {enUso ? 'Bloqueado' : 'Editar'}
                        </button>
                        <button 
                          className="btn btn-ghost btn-sm text-error" 
                          onClick={() => handleDeleteClick(cat)}
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
        title={editingId ? 'Editar Categoria' : 'Nueva Categoria'}
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
            <label>Descripcion</label>
            <textarea
              value={formData.descripcion}
              onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
              maxLength={200}
            />
          </div>
        </form>
      </Modal>

      {/* Confirm Delete Modal */}
      <ConfirmModal
        isOpen={showDeleteModal}
        onClose={() => { setShowDeleteModal(false); setCategoriaToDelete(null); }}
        onConfirm={handleConfirmDelete}
        title="Eliminar Categoria"
        message={`Estas seguro de eliminar "${categoriaToDelete?.nombre}"? Esta accion no se puede deshacer.`}
        confirmText="Eliminar"
        type="danger"
      />
    </div>
  );
};

export default PaginaCategorias;