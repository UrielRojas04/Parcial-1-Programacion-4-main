# README - Guía del Proyecto

## Cómo Ejecutar el Proyecto

### Prerrequisitos

- Python 3.9+
- Node.js 18+
- PostgreSQL (opcional, por defecto usa SQLite)

---

### 1. Ejecutar el Backend

```bash
cd backend

# Crear entorno virtual (opcional)
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python -m uvicorn main:app --reload
```

**URL del Backend:** http://localhost:8000

**Documentación API:** http://localhost:8000/docs

---

### 2. Ejecutar el Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar servidor
npm run dev
```

**URL del Frontend:** http://localhost:5173 (o el puerto que indique la terminal)

---

## Estructura del Proyecto

```
proyecto/
├── backend/           # API REST con FastAPI
│   ├── main.py       # Punto de entrada
│   ├── database.py  # Configuración de BD
│   ├── models/      # Entidades (tablas)
│   ├── schemas/    # Validación de datos
│   ├── routers/    # Endpoints HTTP
│   ├── services/   # Lógica de negocio
│   └── uow/       # Acceso a datos
│
└── frontend/        # App React + Vite
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── services/
    │   ├── context/
    │   └── styles/
    └── package.json
```

---

## Base de Datos

### Esquema de Tablas

```
┌──────────────┐       ┌─────────────┐       ┌──────────────┐
│  CATEGORIA   │ 1:N   │  PRODUCTO  │ N:N  │  INGREDIENTE │
├──────────────┤────── ├─────────────┼──────┼──────────────┤
│ id (PK)      │       │ id (PK)    │      │ id (PK)      │
│ nombre      │       │ nombre    │      │ nombre      │
│ descripcion │       │ precio    │      │ unidad      │
└──────────────┘       │ categoria_id│     └──────────────┘
                       │ (FK)       │────┐
                       └─────────────┘    │
                                      ┌─┴───────────────┐
                       ┌──────────────┤PRODUCTO_INGREDIENTE├
                       │producto_id (PK, FK)             │
                       │ingrediente_id (PK, FK)         │
                       │cantidad                       │
                       └──────────────────────────────┘
```

---

## Endpoints de la API

### Categorías

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/categorias/` | Listar todas |
| GET | `/categorias/{id}` | Obtener por ID |
| POST | `/categorias/` | Crear |
| PUT | `/categorias/{id}` | Editar |
| DELETE | `/categorias/{id}` | Eliminar |
| GET | `/categorias/{id}/en-uso` | Verificar si está en uso |

### Ingredientes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/ingredientes/` | Listar todos |
| GET | `/ingredientes/{id}` | Obtener por ID |
| POST | `/ingredientes/` | Crear |
| PUT | `/ingredientes/{id}` | Editar |
| DELETE | `/ingredientes/{id}` | Eliminar |
| GET | `/ingredientes/{id}/en-uso` | Verificar si está en uso |

### Productos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/productos/` | Listar todos |
| GET | `/productos/{id}` | Obtener por ID |
| POST | `/productos/` | Crear |
| PUT | `/productos/{id}` | Editar |
| DELETE | `/productos/{id}` | Eliminar |
| GET | `/productos/{id}/ingredientes` | Listar ingredientes |
| POST | `/productos/{id}/ingredientes` | Agregar ingrediente |
| DELETE | `/productos/{id}/ingredientes/{ing_id}` | Quitar ingrediente |

---

## Tecnologías Usadas

### Backend
- **FastAPI** - Framework web
- **SQLModel** - ORM (SQLAlchemy + Pydantic)
- **SQLite** - Base de datos (por defecto)
- **Uvicorn** - Servidor ASGI

### Frontend
- **React 18** - Framework UI
- **Vite** - Build tool
- **Axios** - Cliente HTTP
- **TypeScript** - Tipado estático

---

## Notas Importantes

### CORS
El backend está configurado para permitir conexiones desde:
- `http://localhost:5173`
- `http://localhost:5174`

Si el frontend usa otro puerto, agrégalo en `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Búsqueda
La búsqueda es **case-insensitive** (no distingue mayúsculas de minúsculas).

### Validaciones
- Las categorías/ingredientes en uso NO se pueden editar ni eliminar
- Los productos con categoría asignada bloquean la edición de esa categoría
- Los ingredientes asociados a productos bloquean su edición/eliminación