import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============ TIPOS ============
export interface Categoria {
  id: number;
  nombre: string;
  descripcion?: string;
}

export interface Ingrediente {
  id: number;
  nombre: string;
  unidad: string;
}

export interface ProductoIngrediente {
  ingrediente_id: number;
  cantidad: number;
}

export interface Producto {
  id: number;
  nombre: string;
  precio: number;
  descripcion?: string;
  categoria_id?: number;
  ingrediente_links?: ProductoIngrediente[];
}

// ============ CATEGORÍAS ============
export const categoriaService = {
  getAll: (params?: Record<string, unknown>) => 
    api.get<Categoria[]>('/categorias/', { params }),
  getById: (id: number) => 
    api.get<Categoria>(`/categorias/${id}`),
  create: (data: Omit<Categoria, 'id'>) => 
    api.post<Categoria>('/categorias/', data),
  update: (id: number, data: Omit<Categoria, 'id'>) => 
    api.put<Categoria>(`/categorias/${id}`, data),
  delete: (id: number) => 
    api.delete(`/categorias/${id}`),
};

// ============ INGREDIENTES ============
export const ingredienteService = {
  getAll: (params?: Record<string, unknown>) => 
    api.get<Ingrediente[]>('/ingredientes/', { params }),
  getById: (id: number) => 
    api.get<Ingrediente>(`/ingredientes/${id}`),
  create: (data: Omit<Ingrediente, 'id'>) => 
    api.post<Ingrediente>('/ingredientes/', data),
  update: (id: number, data: Omit<Ingrediente, 'id'>) => 
    api.put<Ingrediente>(`/ingredientes/${id}`, data),
  delete: (id: number) => 
    api.delete(`/ingredientes/${id}`),
};

// ============ PRODUCTOS ============
export const productoService = {
  getAll: (params?: Record<string, unknown>) => 
    api.get<Producto[]>('/productos/', { params }),
  getById: (id: number) => 
    api.get<Producto>(`/productos/${id}`),
  create: (data: Omit<Producto, 'id' | 'ingredientes'>) => 
    api.post<Producto>('/productos/', data),
  update: (id: number, data: Omit<Producto, 'id' | 'ingredientes'>) => 
    api.put<Producto>(`/productos/${id}`, data),
  delete: (id: number) => 
    api.delete(`/productos/${id}`),
  agregarIngrediente: (productoId: number, ingredienteData: ProductoIngrediente) =>
    api.post(`/productos/${productoId}/ingredientes`, ingredienteData),
  quitarIngrediente: (productoId: number, ingredienteId: number) =>
    api.delete(`/productos/${productoId}/ingredientes/${ingredienteId}`),
  obtenerIngredientes: (productoId: number) =>
    api.get(`/productos/${productoId}/ingredientes`),
};

export default api;
