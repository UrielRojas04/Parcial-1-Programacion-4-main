import { useState, useEffect, FC } from 'react';
import { productoService, categoriaService, ingredienteService, Categoria, Ingrediente, Producto } from '../services/api';

interface ProductoFormData {
  nombre: string;
  precio: string;
  descripcion: string;
  categoria_id: string;
}

interface IngredienteAgregarData {
  ingrediente_id: string;
  cantidad: string;
}

interface Pagination {
  offset: number;
  limit: number;
}

const PaginaProductos: FC = () => {
  const [productos, setProductos] = useState<Producto[]>([]);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [ingredientes, setIngredientes] = useState<Ingrediente[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [searchNombre, setSearchNombre] = useState('');
  const [filterCategoriaId, setFilterCategoriaId] = useState('');
  const [pagination, setPagination] = useState<Pagination>({ offset: 0, limit: 10 });

  const [formData, setFormData] = useState<ProductoFormData>({
    nombre: '',
    precio: '',
    descripcion: '',
    categoria_id: '',
  });

  // Modal para agregar ingredientes
  const [showIngredientesModal, setShowIngredientesModal] = useState(false);
  const [productoSeleccionado, setProductoSeleccionado] = useState<Producto | null>(null);
  const [ingredienteAgregar, setIngredienteAgregar] = useState<IngredienteAgregarData>({
    ingrediente_id: '',
    cantidad: '',
  });

  // Cargar productos
  const cargarProductos = async (offset: number = 0) => {
    setLoading(true);
    setError('');
    try {
      const response = await productoService.getAll({
        nombre: searchNombre || undefined,
        categoria_id: filterCategoriaId ? parseInt(filterCategoriaId) : undefined,
        offset,
        limit: pagination.limit,
      });
      setProductos(response.data);
      setPagination(prev => ({ ...prev, offset }));
    } catch (err: any) {
      setError('Error al cargar productos: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  // Cargar categorías
  const cargarCategorias = async () => {
    try {
      const response = await categoriaService.getAll({ limit: 100 });
      setCategorias(response.data);
    } catch (err) {
      console.error('Error cargando categorías:', err);
    }
  };

  // Cargar ingredientes
  const cargarIngredientes = async () => {
    try {
      const response = await ingredienteService.getAll({ limit: 100 });
      setIngredientes(response.data);
    } catch (err) {
      console.error('Error cargando ingredientes:', err);
    }
  };

  useEffect(() => {
    cargarProductos();
    cargarCategorias();
    cargarIngredientes();
  }, [searchNombre, filterCategoriaId]);

  // Manejar submit del formulario de producto
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!formData.nombre.trim()) {
      setError('El nombre es requerido');
      return;
    }

    if (!formData.precio || parseFloat(formData.precio) <= 0) {
      setError('El precio debe ser mayor a 0');
      return;
    }

    try {
      const dataToSend = {
        nombre: formData.nombre,
        precio: parseFloat(formData.precio),
        descripcion: formData.descripcion || undefined,
        categoria_id: formData.categoria_id ? parseInt(formData.categoria_id) : undefined,
      };

      if (editingId) {
        await productoService.update(editingId, dataToSend);
        setSuccess('Producto actualizado correctamente');
      } else {
        await productoService.create(dataToSend);
        setSuccess('Producto creado correctamente');
      }
      resetForm();
      cargarProductos(0);
    } catch (err: any) {
      setError('Error: ' + (err.response?.data?.detail || err.message));
    }
  };

  // Editar producto
  const handleEdit = (producto: Producto) => {
    setFormData({
      nombre: producto.nombre,
      precio: producto.precio.toString(),
      descripcion: producto.descripcion || '',
      categoria_id: producto.categoria_id?.toString() || '',
    });
    setEditingId(producto.id);
    setShowForm(true);
  };

  // Eliminar producto
  const handleDelete = async (id: number) => {
    if (!confirm('¿Está seguro de que desea eliminar este producto?')) return;

    try {
      await productoService.delete(id);
      setSuccess('Producto eliminado correctamente');
      cargarProductos(0);
    } catch (err: any) {
      setError('Error: ' + (err.response?.data?.detail || err.message));
    }
  };

  // Agregar ingrediente a producto
  const handleAgregarIngrediente = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!ingredienteAgregar.ingrediente_id) {
      setError('Seleccione un ingrediente');
      return;
    }

    if (!ingredienteAgregar.cantidad || parseFloat(ingredienteAgregar.cantidad) <= 0) {
      setError('La cantidad debe ser mayor a 0');
      return;
    }

    try {
      if (productoSeleccionado) {
        await productoService.agregarIngrediente(
          productoSeleccionado.id,
          {
            ingrediente_id: parseInt(ingredienteAgregar.ingrediente_id),
            cantidad: parseFloat(ingredienteAgregar.cantidad),
          }
        );
        setSuccess('Ingrediente agregado correctamente');
        setIngredienteAgregar({ ingrediente_id: '', cantidad: '' });
        cargarProductos(pagination.offset);
        setProductoSeleccionado(null);
      }
    } catch (err: any) {
      setError('Error: ' + (err.response?.data?.detail || err.message));
    }
  };

  // Quitar ingrediente de producto
  const handleQuitarIngrediente = async (productoId: number, ingredienteId: number) => {
    if (!confirm('¿Desea quitar este ingrediente del producto?')) return;

    try {
      await productoService.quitarIngrediente(productoId, ingredienteId);
      setSuccess('Ingrediente removido correctamente');
      cargarProductos(pagination.offset);
    } catch (err: any) {
      setError('Error: ' + (err.response?.data?.detail || err.message));
    }
  };

  // Reset del formulario
  const resetForm = () => {
    setFormData({ nombre: '', precio: '', descripcion: '', categoria_id: '' });
    setEditingId(null);
    setShowForm(false);
  };

  // Obtener nombre de categoría
  const getNombreCategoria = (categoriaId?: number): string => {
    if (!categoriaId) return 'Sin categoría';
    const cat = categorias.find(c => c.id === categoriaId);
    return cat ? cat.nombre : 'Desconocido';
  };

  // Obtener nombre de ingrediente
  const getNombreIngrediente = (ingredienteId: number): string => {
    const ing = ingredientes.find(i => i.id === ingredienteId);
    return ing ? ing.nombre : 'Desconocido';
  };

  // Obtener unidad de ingrediente
  const getUnidadIngrediente = (ingredienteId: number): string => {
    const ing = ingredientes.find(i => i.id === ingredienteId);
    return ing ? ing.unidad : '';
  };

  // Obtener ingredientes disponibles (no agregados al producto)
  const getIngredientesDisponibles = (): Ingrediente[] => {
    if (!productoSeleccionado) return ingredientes;
    const ingredientesProducto = productoSeleccionado.ingrediente_links?.map(p => p.ingrediente_id) || [];
    return ingredientes.filter(ing => !ingredientesProducto.includes(ing.id));
  };

  return (
    <div className="container">
      <h2 className="section-title">📦 Gestión de Productos</h2>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {/* Filtros */}
      <div className="form-row">
        <div className="form-group">
          <input
            type="text"
            placeholder="Buscar producto por nombre..."
            value={searchNombre}
            onChange={(e) => setSearchNombre(e.target.value)}
          />
        </div>
        <div className="form-group">
          <select
            value={filterCategoriaId}
            onChange={(e) => setFilterCategoriaId(e.target.value)}
          >
            <option value="">Todas las categorías</option>
            {categorias.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.nombre}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Botón agregar */}
      <button className="btn btn-primary" onClick={() => { resetForm(); setShowForm(true); }}>
        ➕ Nuevo Producto
      </button>

      {/* Formulario modal - Crear/Editar Producto */}
      {showForm && (
        <div className="modal-overlay" onClick={resetForm}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">
                {editingId ? '✏️ Editar Producto' : '➕ Nuevo Producto'}
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
                  maxLength={100}
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
                  />
                </div>

                <div className="form-group">
                  <label>Categoría</label>
                  <select
                    value={formData.categoria_id}
                    onChange={(e) => setFormData({ ...formData, categoria_id: e.target.value })}
                  >
                    <option value="">Sin categoría</option>
                    {categorias.map(cat => (
                      <option key={cat.id} value={cat.id}>{cat.nombre}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Descripción</label>
                <textarea
                  value={formData.descripcion}
                  onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                  maxLength={300}
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

      {/* Modal para agregar ingredientes */}
      {showIngredientesModal && productoSeleccionado && (
        <div className="modal-overlay" onClick={() => { setShowIngredientesModal(false); setProductoSeleccionado(null); }}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">➕ Agregar Ingrediente a "{productoSeleccionado.nombre}"</h3>
              <button className="modal-close" onClick={() => { setShowIngredientesModal(false); setProductoSeleccionado(null); }}>✕</button>
            </div>

            {/* Ingredientes actuales */}
            {productoSeleccionado.ingrediente_links && productoSeleccionado.ingrediente_links.length > 0 && (
              <div className="ingredientes-list">
                <h4>📋 Ingredientes actuales:</h4>
                {productoSeleccionado.ingrediente_links.map((pi) => (
                  <div key={pi.ingrediente_id} className="ingrediente-item">
                    <div className="ingrediente-info">
                      {getNombreIngrediente(pi.ingrediente_id)}
                    </div>
                    <div className="ingrediente-cantidad">
                      {pi.cantidad} {getUnidadIngrediente(pi.ingrediente_id)}
                    </div>
                    <button
                      type="button"
                      className="btn btn-danger btn-sm"
                      onClick={() => handleQuitarIngrediente(productoSeleccionado.id, pi.ingrediente_id)}
                    >
                      🗑️
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Formulario agregar ingrediente */}
            <form onSubmit={handleAgregarIngrediente}>
              <div className="form-group">
                <label>Ingrediente *</label>
                <select
                  value={ingredienteAgregar.ingrediente_id}
                  onChange={(e) => setIngredienteAgregar({ ...ingredienteAgregar, ingrediente_id: e.target.value })}
                >
                  <option value="">Seleccionar ingrediente...</option>
                  {getIngredientesDisponibles().map(ing => (
                    <option key={ing.id} value={ing.id}>{ing.nombre} ({ing.unidad})</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Cantidad *</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={ingredienteAgregar.cantidad}
                  onChange={(e) => setIngredienteAgregar({ ...ingredienteAgregar, cantidad: e.target.value })}
                  placeholder="Ej: 100"
                />
              </div>

              <div className="btn-group">
                <button type="submit" className="btn btn-success">
                  ➕ Agregar
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => { setShowIngredientesModal(false); setProductoSeleccionado(null); }}
                >
                  ✕ Cerrar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Tabla de productos */}
      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
          <p>Cargando...</p>
        </div>
      ) : (
        <>
          {productos.length === 0 ? (
            <div className="alert alert-info">No hay productos para mostrar</div>
          ) : (
            <div style={{ overflowX: 'auto', marginTop: '20px' }}>
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Precio</th>
                    <th>Categoría</th>
                    <th>Ingredientes</th>
                    <th>Descripción</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {productos.map((producto) => (
                    <tr key={producto.id}>
                      <td>#{producto.id}</td>
                      <td>{producto.nombre}</td>
                      <td>${producto.precio.toFixed(2)}</td>
                      <td>{getNombreCategoria(producto.categoria_id)}</td>
                      <td>
                        {producto.ingrediente_links && producto.ingrediente_links.length > 0 ? (
                            <div style={{ fontSize: '12px' }}>
                            {producto.ingrediente_links.map((pi) => (
                                <div key={pi.ingrediente_id}>
                                🥗 {getNombreIngrediente(pi.ingrediente_id)} — {pi.cantidad} {getUnidadIngrediente(pi.ingrediente_id)}
                                </div>
                            ))}
                            </div>
                        ) : (
                            <span style={{ color: '#999' }}>Sin ingredientes</span>
                        )}
                        </td>
                      <td>
                        <button
                          className="btn btn-primary btn-sm"
                          onClick={() => handleEdit(producto)}
                          title="Editar"
                        >
                          ✏️
                        </button>
                        <button
                            className="btn btn-success btn-sm"
                            onClick={async () => {
                                const response = await productoService.getById(producto.id);
                                setProductoSeleccionado(response.data);
                                setShowIngredientesModal(true);
                                setIngredienteAgregar({ ingrediente_id: '', cantidad: '' });
                                setError('');
                                setSuccess('');
                            }}
                            title="Ingredientes"
                            >
                            🥘
                            </button>
                        <button
                          className="btn btn-danger btn-sm"
                          onClick={() => handleDelete(producto.id)}
                          title="Eliminar"
                        >
                          🗑️
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Paginación */}
          <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
            <button
              className="btn btn-secondary"
              onClick={() => cargarProductos(Math.max(0, pagination.offset - pagination.limit))}
              disabled={pagination.offset === 0}
            >
              ← Anterior
            </button>
            <span style={{ alignSelf: 'center', color: '#666' }}>
              Página {Math.floor(pagination.offset / pagination.limit) + 1}
            </span>
            <button
              className="btn btn-secondary"
              onClick={() => cargarProductos(pagination.offset + pagination.limit)}
              disabled={productos.length < pagination.limit}
            >
              Siguiente →
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default PaginaProductos;
