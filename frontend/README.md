# Frontend - Gestor de Productos y Categorías

Un frontend moderno construido con **React + Vite + TypeScript** que consume todos los endpoints del backend FastAPI para gestionar:

- ✅ **Categorías** (CRUD completo)
- ✅ **Productos** (CRUD + relación con categorías)
- ✅ **Ingredientes** (CRUD completo)
- ✅ **Relaciones N:N** (Producto ↔ Ingrediente)

## 🚀 Requisitos Previos

- **Node.js** (v16 o superior)
- **npm** (incluido con Node.js)
- El **backend FastAPI** debe estar ejecutándose en `http://localhost:8000`

## 📦 Instalación

### 1. Navegar a la carpeta del frontend

```bash
cd frontend
```

### 2. Instalar dependencias

```bash
npm install
```

## 🎮 Ejecución

### Modo Desarrollo

```bash
npm run dev
```

El servidor se iniciará en: **http://localhost:5173**

### Modo Producción

```bash
npm run build
npm run preview
```

## 📋 Características Principales

### 🏷️ Gestión de Categorías
- Crear nuevas categorías
- Editar categorías existentes
- Eliminar categorías
- Buscar por nombre
- Paginación

### 📦 Gestión de Productos
- Crear productos (nombre, precio, descripción, categoría)
- Editar productos
- Eliminar productos
- Buscar por nombre
- Filtrar por categoría
- **Agregar/Quitar ingredientes** a productos (relación N:N)
- Ver ingredientes de cada producto
- Paginación

### 🥘 Gestión de Ingredientes
- Crear ingredientes (nombre, unidad)
- Editar ingredientes
- Eliminar ingredientes
- Buscar por nombre
- Paginación

## 🔗 Relaciones Implementadas

### 1️⃣ Categoría → Producto (1:N)
- Un producto se asigna a **una sola categoría**
- Una categoría puede tener **muchos productos**
- En el frontend: Filtro de productos por categoría

### 2️⃣ Producto ↔ Ingrediente (N:N)
- Un producto puede tener **muchos ingredientes**
- Un ingrediente puede estar en **muchos productos**
- Cada relación tiene una **cantidad** asociada
- En el frontend: Modal para gestionar ingredientes de un producto

## 📡 Endpoints Consumidos

### Categorías
- `GET /categorias/` - Listar categorías
- `GET /categorias/{id}` - Obtener categoría
- `POST /categorias/` - Crear categoría
- `PUT /categorias/{id}` - Editar categoría
- `DELETE /categorias/{id}` - Eliminar categoría

### Ingredientes
- `GET /ingredientes/` - Listar ingredientes
- `GET /ingredientes/{id}` - Obtener ingrediente
- `POST /ingredientes/` - Crear ingrediente
- `PUT /ingredientes/{id}` - Editar ingrediente
- `DELETE /ingredientes/{id}` - Eliminar ingrediente

### Productos
- `GET /productos/` - Listar productos (con filtros)
- `GET /productos/{id}` - Obtener producto
- `POST /productos/` - Crear producto
- `PUT /productos/{id}` - Editar producto
- `DELETE /productos/{id}` - Eliminar producto
- `POST /productos/{id}/ingredientes` - Agregar ingrediente
- `DELETE /productos/{id}/ingredientes/{ingrediente_id}` - Quitar ingrediente

## 🎨 Tecnologías Utilizadas

- **React 18** - Biblioteca de UI
- **TypeScript 5** - Lenguaje tipado
- **Vite** - Herramienta de build y dev server
- **Axios** - Cliente HTTP para consumir API
- **CSS3** - Estilos responsivos

## 📱 Responsive Design

La aplicación es completamente **responsive** y funciona en:
- 📱 Móviles
- 📱 Tablets
- 🖥️ Computadoras

## 🗂️ Estructura de Carpetas

```
frontend/
├── src/
│   ├── components/
│   │   ├── Navegacion.tsx      # Navegación principal (TypeScript)
│   │   └── Navegacion.css      # Estilos navegación
│   ├── pages/
│   │   ├── PaginaCategorias.tsx   # Página de categorías (TypeScript)
│   │   ├── PaginaIngredientes.tsx # Página de ingredientes (TypeScript)
│   │   └── PaginaProductos.tsx    # Página de productos (TypeScript)
│   ├── services/
│   │   └── api.ts              # Cliente API con tipos (TypeScript)
│   ├── App.tsx                 # Componente raíz (TypeScript)
│   ├── App.css                 # Estilos principales
│   └── main.tsx                # Punto de entrada (TypeScript)
├── tsconfig.json               # Configuración TypeScript
├── tsconfig.node.json          # Config TypeScript para Vite
├── vite.config.ts              # Config Vite (TypeScript)
├── index.html
├── package.json
└── README.md
```

## 🔌 Configuración de API

El cliente API está configurado en `src/services/api.ts` con tipos TypeScript:

```typescript
const API_BASE_URL = 'http://localhost:8000';
```

Para cambiar la URL del backend, edita esta línea.

## 🛠️ Desarrollo

### Agregar una nueva página

1. Crear archivo en `src/pages/MiPagina.tsx`
2. Importar en `src/App.tsx`
3. Agregar ruta en el switch de `renderPagina()`
4. Agregar botón en `Navegacion.tsx`

### Agregar un nuevo servicio

Crear métodos con tipos en `src/services/api.ts`:

```typescript
export const miServicio = {
  getAll: (params?: Record<string, unknown>) => 
    api.get<MiTipo[]>('/endpoint/', { params }),
  getById: (id: number) => 
    api.get<MiTipo>(`/endpoint/${id}`),
  create: (data: Omit<MiTipo, 'id'>) => 
    api.post<MiTipo>('/endpoint/', data),
  update: (id: number, data: Omit<MiTipo, 'id'>) => 
    api.put<MiTipo>(`/endpoint/${id}`, data),
  delete: (id: number) => 
    api.delete(`/endpoint/${id}`),
};
```

## 📝 Notas Importantes

- El backend debe estar ejecutándose en `http://localhost:8000`
- CORS está habilitado en el backend para `http://localhost:5173`
- Los errores de API se muestran en alertas rojas
- Los éxitos se muestran en alertas verdes
- TypeScript proporciona verificación de tipos en tiempo de desarrollo

## 🐛 Solución de Problemas

### "Error al conectar con la API"
- Verifica que el backend esté ejecutándose en `http://localhost:8000`
- Revisa la consola del navegador (F12) para más detalles

### Los cambios no se reflejan
- Prueba hacer un hard refresh: `Ctrl + Shift + R` (Windows/Linux) o `Cmd + Shift + R` (Mac)

### CORS error
- Verifica que el backend tenga CORS habilitado para `http://localhost:5173`

### Errores de TypeScript
- Ejecuta `npm run build` para verificar errores de tipo
- Asegúrate de que todos los tipos estén correctamente importados

## 📄 Licencia

Proyecto educativo - Parcial 1 Programación 4

---

**¡Listo para usar con TypeScript!** 🚀

HOLA DESDE FRONT