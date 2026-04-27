import { useState, useEffect, FC } from 'react';
import { productoService, categoriaService, ingredienteService, Categoria, Ingrediente, Producto } from '../services/api';
import { useToast } from '../context/ToastContext';
import Modal from '../components/Modal';
import ConfirmModal from '../components/ConfirmModal';

interface ProductoFormData {
  nombre: string;
  precio: string;
  descripcion: string;
  categoria_id: string;
}

interface IngredienteFormData {
  ingrediente_id: string;
  cantidad: string;
}

const PaginaProductos: FC = () => {
  const [productos, setProductos] = useState<Producto[]>([]);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [ingredientes, setIngredientes] = useState<Ingrediente[]>([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showRemoveIngModal, setShowRemoveIngModal] = useState(false);
  const [productoToDelete, setProductoToDelete] = useState<Producto | null>(null);
  const [ingredienteToRemove, setIngredienteToRemove] = useState<{productoId: number, ingId: number, nombre: string, cantidad: number} | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [showIngredientesModal, setShowIngredientesModal] = useState(false);
  const [productoSeleccionado, setProductoSeleccionado] = useState<Producto | null>(null);
  const [searchNombre, setSearchNombre] = useState('');
  const [filterCategoriaId, setFilterCategoriaId] = useState('');
  
  const [formData, setFormData] = useState<ProductoFormData>({
    nombre: '',
    precio: '',
    descripcion: '',
    categoria_id: '',
  });

  const [ingredienteForm, setIngredienteForm] = useState<IngredienteFormData>({
    ingrediente_id: '',
    cantidad: '',
  });

  const { showToast } = useToast();

  const cargarProductos = async () => {
    setLoading(true);
    try {
      const response = await productoService.getAll({
        nombre: searchNombre || undefined,
        categoria_id: filterCategoriaId ? parseInt(filterCategoriaId) : undefined,
        limit: 100
      });
      setProductos(response.data);
    } catch {
      showToast('error', 'Error al cargar productos');
    } finally {
      setLoading(false);
    }
  };

  const cargarCategorias = async () => {
    try {
      const response = await categoriaService.getAll({ limit: 100 });
      setCategorias(response.data);
    } catch {
      console.error('Error cargando categorias');
    }
  };

  const cargarIngredientesAPI = async () => {
    try {
      const response = await ingredienteService.getAll({ limit: 100 });
      setIngredientes(response.data);
    } catch {
      console.error('Error cargando ingredientes');
    }
  };

  useEffect(() => {
    cargarProductos();
    cargarCategorias();
    cargarIngredientesAPI();
  }, [searchNombre, filterCategoriaId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const nombreTrim = formData.nombre.trim();
    if (!nombreTrim) {
      showToast('error', 'El nombre es requerido');
      return;
    }
    if (!formData.precio || parseFloat(formData.precio) <= 0) {
      showToast('error', 'El precio debe ser mayor a 0');
      return;
    }

    try {
      const dataToSend = {
        nombre: nombreTrim,
        precio: parseFloat(formData.precio),
        descripcion: formData.descripcion || undefined,
        categoria_id: formData.categoria_id ? parseInt(formData.categoria_id) : undefined,
      };

      if (editingId) {
        await productoService.update(editingId, dataToSend);
        showToast('success', 'Producto actualizado');
      } else {
        await productoService.create(dataToSend);
        showToast('success', 'Producto creado');
      }
      resetForm();
      cargarProductos();
    } catch {
      showToast('error', 'Error al guardar');
    }
  };

  const handleEdit = (producto: Producto) => {
    setFormData({
      nombre: producto.nombre,
      precio: producto.precio.toString(),
      descripcion: producto.descripcion || '',
      categoria_id: producto.categoria_id?.toString() || '',
    });
    setEditingId(producto.id);
    setShowModal(true);
  };

  const handleDeleteClick = (producto: Producto) => {
    setProductoToDelete(producto);
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = async () => {
    if (!productoToDelete) return;
    try {
      await productoService.delete(productoToDelete.id);
      showToast('success', 'Producto eliminado');
      cargarProductos();
    } catch {
      showToast('error', 'No se puede eliminar');
    }
    setProductoToDelete(null);
  };

  const resetForm = () => {
    setFormData({ nombre: '', precio: '', descripcion: '', categoria_id: '' });
    setEditingId(null);
    setShowModal(false);
  };

  // Open ingredients modal
  const openIngredientesModal = async (producto: Producto) => {
    try {
      const response = await productoService.getById(producto.id);
      setProductoSeleccionado(response.data);
      setShowIngredientesModal(true);
      setIngredienteForm({ ingrediente_id: '', cantidad: '' });
    } catch {
      showToast('error', 'Error al cargar producto');
    }
  };

  const handleAgregarIngrediente = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ingredienteForm.ingrediente_id || !ingredienteForm.cantidad) {
      showToast('error', 'Complete todos los campos');
      return;
    }

    try {
      await productoService.agregarIngrediente(
        productoSeleccionado!.id,
        {
          ingrediente_id: parseInt(ingredienteForm.ingrediente_id),
          cantidad: parseFloat(ingredienteForm.cantidad),
        }
      );
      showToast('success', 'Ingrediente agregado');
      const response = await productoService.getById(productoSeleccionado!.id);
      setProductoSeleccionado(response.data);
      cargarProductos();
      setIngredienteForm({ ingrediente_id: '', cantidad: '' });
    } catch {
      showToast('error', 'Error al agregar ingrediente');
    }
  };

  const handleRemoveIngClick = (ingredienteId: number, nombre: string, cantidad: number) => {
    setIngredienteToRemove({ productoId: productoSeleccionado!.id, ingId: ingredienteId, nombre, cantidad });
    setShowRemoveIngModal(true);
  };

  const handleConfirmRemoveIng = async () => {
    if (!ingredienteToRemove) return;
    try {
      await productoService.quitarIngrediente(ingredienteToRemove.productoId, ingredienteToRemove.ingId);
      showToast('success', 'Ingrediente removido');
      // Recargar producto con ingredientes actualizados
      const response = await productoService.getById(ingredienteToRemove.productoId);
      setProductoSeleccionado(response.data);
      // Also reload the productos list to show updated ingredients
      cargarProductos();
    } catch {
      showToast('error', 'Error al remover ingrediente');
    }
    setIngredienteToRemove(null);
  };

  const getNombreCategoria = (categoriaId?: number): string => {
    if (!categoriaId) return 'Sin categoria';
    const cat = categorias.find(c => c.id === categoriaId);
    return cat ? cat.nombre : 'Desconocido';
  };

  const getNombreIngrediente = (ingredienteId: number): string => {
    const ing = ingredientes.find(i => i.id === ingredienteId);
    return ing ? ing.nombre : 'Desconocido';
  };

  const getUnidadIngrediente = (ingredienteId: number): string => {
    const ing = ingredientes.find(i => i.id === ingredienteId);
    return ing ? ing.unidad : '';
  };

  const getIngredientesDisponibles = (): Ingrediente[] => {
    if (!productoSeleccionado) return ingredientes;
    const ids = productoSeleccionado.ingrediente_links?.map(p => p.ingrediente_id) || [];
    return ingredientes.filter(ing => !ids.includes(ing.id));
  };

  const formatPrecio = (precio: number): string => {
    return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(precio);
  };

  // Filter by case-insensitive search + category + ingredient name
  const filteredProductos = productos.filter(p => {
    const search = searchNombre.toLowerCase();
    if (!search) return true;
    
    if (p.nombre.toLowerCase().includes(search)) return true;
    
    // Search in category name
    if (p.categoria_id) {
      const cat = categorias.find(c => c.id === p.categoria_id);
      if (cat && cat.nombre.toLowerCase().includes(search)) return true;
    }
    
    // Search in ingredient names
    if (p.ingrediente_links && p.ingrediente_links.length > 0) {
      for (const pi of p.ingrediente_links) {
        const ingNombre = getNombreIngrediente(pi.ingrediente_id).toLowerCase();
        if (ingNombre.includes(search)) return true;
      }
    }
    
    return false;
  });

  return (
    <div className="container">
      <div className="header-actions">
        <h2 className="header-title">Productos</h2>
        
        <div className="header-toolbar">
          <input
            type="text"
            className="search-input"
            placeholder="Buscar por nombre, categoria o ingrediente..."
            value={searchNombre}
            onChange={(e) => setSearchNombre(e.target.value)}
          />
          <select
            className="search-select"
            value={filterCategoriaId}
            onChange={(e) => setFilterCategoriaId(e.target.value)}
          >
            <option value="">Todas las categorias</option>
            {categorias.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.nombre}</option>
            ))}
          </select>
          <button className="btn btn-primary" onClick={() => { resetForm(); setShowModal(true); }}>
            + Nuevo
          </button>
        </div>
      </div>

      {loading ? (
        <div className="loading-container">
          <div className="spinner"></div>
        </div>
      ) : filteredProductos.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-title">
            {searchNombre || filterCategoriaId ? 'No se encontraron productos' : 'No hay productos'}
          </div>
          <div className="empty-state-text">
            {searchNombre || filterCategoriaId ? 'Intenta con otros terminos' : 'Crea tu primer producto'}
          </div>
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Precio</th>
                <th>Categoria</th>
                <th>Ingredientes</th>
                <th style={{ width: '140px' }}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filteredProductos.map((prod) => (
                <tr key={prod.id}>
                  <td className="font-medium">{prod.nombre}</td>
                  <td>{formatPrecio(prod.precio)}</td>
                  <td>
                    <span className="badge badge-secondary">{getNombreCategoria(prod.categoria_id)}</span>
                  </td>
                  <td>
                    {prod.ingrediente_links && prod.ingrediente_links.length > 0 ? (
                      <div className="ingredientes-mini">
                        {prod.ingrediente_links.map((pi) => (
                          <div key={pi.ingrediente_id} className="ingrediente-chip">
                            <span>{getNombreIngrediente(pi.ingrediente_id)}</span>
                            <span className="cantidad">({pi.cantidad})</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <span className="text-muted">Sin ingredientes</span>
                    )}
                  </td>
                  <td>
                    <div className="actions-bar">
                      <button className="btn btn-ghost btn-sm" onClick={() => openIngredientesModal(prod)}>
                        Ing
                      </button>
                      <button className="btn btn-ghost btn-sm" onClick={() => handleEdit(prod)}>
                        Editar
                      </button>
                      <button className="btn btn-ghost btn-sm text-error" onClick={() => handleDeleteClick(prod)}>
                        Eliminar
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal
        isOpen={showModal}
        onClose={resetForm}
        title={editingId ? 'Editar Producto' : 'Nuevo Producto'}
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
              maxLength={100}
              autoFocus
            />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Precio *</label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={formData.precio}
                onChange={(e) => setFormData({ ...formData, precio: e.target.value })}
                placeholder="0.00"
              />
            </div>
            <div className="form-group">
              <label>Categoria</label>
              <select
                value={formData.categoria_id}
                onChange={(e) => setFormData({ ...formData, categoria_id: e.target.value })}
              >
                <option value="">Sin categoria</option>
                {categorias.map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.nombre}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="form-group">
            <label>Descripcion</label>
            <textarea
              value={formData.descripcion}
              onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
              maxLength={300}
            />
          </div>
        </form>
      </Modal>

      <Modal
        isOpen={showIngredientesModal}
        onClose={() => { setShowIngredientesModal(false); setProductoSeleccionado(null); }}
        title={`Ingredientes: ${productoSeleccionado?.nombre}`}
        footer={
          <button className="btn btn-secondary" onClick={() => { setShowIngredientesModal(false); setProductoSeleccionado(null); }}>
            Cerrar
          </button>
        }
      >
        {productoSeleccionado?.ingrediente_links && productoSeleccionado.ingrediente_links.length > 0 && (
          <div className="ingredientes-list">
            <h4 className="mb-sm">Ingredientes actuales:</h4>
            {productoSeleccionado.ingrediente_links.map((pi) => (
              <div key={pi.ingrediente_id} className="ingrediente-item">
                <div className="ingrediente-info">
                  <strong>{getNombreIngrediente(pi.ingrediente_id)}</strong>
                  <span className="text-muted"> - {pi.cantidad} {getUnidadIngrediente(pi.ingrediente_id)}</span>
                </div>
                <button
                  className="btn btn-ghost btn-sm text-error"
                  onClick={() => handleRemoveIngClick(pi.ingrediente_id, getNombreIngrediente(pi.ingrediente_id), pi.cantidad)}
                >
                  Eliminar
                </button>
              </div>
            ))}
          </div>
        )}

        {getIngredientesDisponibles().length > 0 ? (
          <form onSubmit={handleAgregarIngrediente} className="mt-md">
            <div className="form-group">
              <label>Agregar ingrediente</label>
              <select
                value={ingredienteForm.ingrediente_id}
                onChange={(e) => setIngredienteForm({ ...ingredienteForm, ingrediente_id: e.target.value })}
              >
                <option value="">Seleccionar...</option>
                {getIngredientesDisponibles().map(ing => (
                  <option key={ing.id} value={ing.id}>{ing.nombre} ({ing.unidad})</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Cantidad</label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={ingredienteForm.cantidad}
                onChange={(e) => setIngredienteForm({ ...ingredienteForm, cantidad: e.target.value })}
                placeholder="Cantidad"
              />
            </div>
            <button type="submit" className="btn btn-success w-full">
              Agregar
            </button>
          </form>
        ) : (
          <div className="empty-state mt-md">
            <div className="empty-state-text">Todos los ingredientes ya fueron agregados</div>
          </div>
        )}
      </Modal>

      <ConfirmModal
        isOpen={showDeleteModal}
        onClose={() => { setShowDeleteModal(false); setProductoToDelete(null); }}
        onConfirm={handleConfirmDelete}
        title="Eliminar Producto"
        message={`Estas seguro de eliminar "${productoToDelete?.nombre}"? Esta accion no se puede deshacer.`}
        confirmText="Eliminar"
        type="danger"
      />

      {/* Confirm Remove Ingredient */}
      <ConfirmModal
        isOpen={showRemoveIngModal}
        onClose={() => { setShowRemoveIngModal(false); setIngredienteToRemove(null); }}
        onConfirm={handleConfirmRemoveIng}
        title="Quitar Ingrediente"
        message={`Quitar "${ingredienteToRemove?.nombre}" (${ingredienteToRemove?.cantidad}) de este producto?`}
        confirmText="Quitar"
        type="warning"
      />
    </div>
  );
};

export default PaginaProductos;