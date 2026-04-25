# 📚 README - Guía Completa del Proyecto

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Módulos - Explicación Detallada](#módulos---explicación-detallada)
4. [Flujo de Ejecución](#flujo-de-ejecución)
5. [Base de Datos](#base-de-datos)
6. [Cómo Usar la API](#cómo-usar-la-api)
7. [Ejemplos de Código](#ejemplos-de-código)
8. [Agregar Nuevas Funcionalidades](#agregar-nuevas-funcionalidades)

---

## Descripción General

Este es un **backend API REST** construido con **FastAPI** y **SQLModel** que gestiona:
- **Categorías** de productos
- **Productos** con precios y descripciones
- **Ingredientes** con unidades de medida
- **Relaciones** entre productos e ingredientes (N:N)

### Stack Tecnológico

| Componente | Tecnología |
|-----------|-----------|
| Framework Web | FastAPI |
| ORM / SQLModel | SQLAlchemy + Pydantic |
| Base de Datos | SQL (configurable: PostgreSQL, MySQL, SQLite) |
| Validación | Pydantic |
| Control de Acceso | CORS |

---

## Estructura del Proyecto

```
backend/
│
├── main.py                    # 🎯 Punto de entrada de la aplicación
├── database.py                # 🗄️ Configuración de conexión a BD
│
├── models/                    # 📦 Entidades (estructuras de datos)
│   ├── __init__.py
│   ├── categoria.py           # Modelo de Categoría
│   ├── producto.py            # Modelo de Producto
│   ├── ingrediente.py         # Modelo de Ingrediente
│   └── producto_ingrediente.py # Modelo de relación N:N
│
├── schemas/                   # ✅ Validación de datos (entrada/salida)
│   ├── __init__.py
│   └── schemas.py             # Esquemas Pydantic
│
├── routers/                   # 🛣️ Endpoints HTTP (controladores)
│   ├── __init__.py
│   ├── categorias.py          # Endpoints: GET, POST, PUT, DELETE
│   ├── ingredientes.py        # Endpoints: GET, POST, PUT, DELETE
│   └── productos.py           # Endpoints: GET, POST, PUT, DELETE
│
├── services/                  # 💼 Lógica de negocio
│   ├── __init__.py
│   ├── categoria_service.py   # Lógica: búsquedas, validaciones
│   ├── ingrediente_service.py # Lógica: búsquedas, validaciones
│   └── producto_service.py    # Lógica: búsquedas, validaciones
│
└── uow/                       # 🔄 Unit of Work (acceso a datos)
    ├── __init__.py
    ├── repository.py          # Clase base genérica (CRUD)
    ├── categoria_repository.py # Operaciones específicas
    ├── ingrediente_repository.py
    ├── producto_repository.py
    └── unit_of_work.py        # Gestor de transacciones
```

---

## Módulos - Explicación Detallada

### 1️⃣ **main.py** - Punto de Entrada

**¿Qué hace?** Configura la aplicación FastAPI e incluye todos los routers.

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_db
from routers import categorias, ingredientes, productos

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()  # Crea tablas al iniciar
    yield

app = FastAPI(lifespan=lifespan)

# Permite solicitudes desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluye todos los routers
app.include_router(categorias.router)
app.include_router(ingredientes.router)
app.include_router(productos.router)

@app.get("/")
def root():
    return {"message": "Api funcionando correctamente"}
```

**Responsabilidades:**
- ✅ Inicializar FastAPI
- ✅ Configurar CORS (comunicación con frontend)
- ✅ Crear tablas en la BD al iniciar
- ✅ Incluir todos los routers de endpoints

---

### 2️⃣ **database.py** - Configuración de Base de Datos

**¿Qué hace?** Gestiona la conexión a la BD y proporciona sesiones.

```python
from sqlmodel import create_engine, SQLModel, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

def create_db():
    """Crea todas las tablas en la BD"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Proporciona una sesión de BD para cada request"""
    with Session(engine) as session:
        yield session
```

**Responsabilidades:**
- ✅ Crear conexión a la BD
- ✅ Crear tablas automáticamente
- ✅ Proporcionar sesiones para queries

---

### 3️⃣ **models/** - Entidades de la Base de Datos

#### **modelo/categoria.py**
```python
from sqlmodel import SQLModel, Field, Relationship

class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=2, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=200)
    
    # Relación 1:N
    productos: List["Producto"] = Relationship(back_populates="categoria")
```

**Qué es:**
- Representación de una **categoría** en la BD
- Hereda de `SQLModel` → combina Pydantic + SQLAlchemy
- `table=True` → crea tabla en la BD

**Campos:**
| Campo | Tipo | Validación |
|-------|------|-----------|
| `id` | int | PK (auto) |
| `nombre` | str | 2-50 caracteres |
| `descripcion` | str | Máx 200 caracteres, opcional |

**Relaciones:**
- `productos` → Lista de productos de esta categoría

---

#### **modelo/producto.py**
```python
class Producto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=2, max_length=100)
    precio: float = Field(gt=0)
    descripcion: Optional[str] = Field(default=None, max_length=300)
    
    # FK a Categoría
    categoria_id: Optional[int] = Field(default=None, foreign_key="categoria.id")
    categoria: Optional["Categoria"] = Relationship(back_populates="productos")
    
    # Relación N:N
    ingrediente_links: List["ProductoIngrediente"] = Relationship(back_populates="producto")
```

**Campos:**
| Campo | Tipo | Validación |
|-------|------|-----------|
| `id` | int | PK (auto) |
| `nombre` | str | 2-100 caracteres |
| `precio` | float | Mayor a 0 |
| `descripcion` | str | Máx 300 caracteres, opcional |
| `categoria_id` | int | FK → categoria.id, opcional |

**Relaciones:**
- `categoria` → Categoría a la que pertenece (1:N)
- `ingrediente_links` → Ingredientes de este producto (N:N)

---

#### **modelo/ingrediente.py**
```python
class Ingrediente(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=2, max_length=50)
    unidad: str = Field(max_length=20)
    
    # Relación N:N
    producto_links: List["ProductoIngrediente"] = Relationship(back_populates="ingrediente")
```

**Campos:**
| Campo | Tipo | Validación |
|-------|------|-----------|
| `id` | int | PK (auto) |
| `nombre` | str | 2-50 caracteres |
| `unidad` | str | Máx 20 caracteres |

**Relaciones:**
- `producto_links` → Productos que contienen este ingrediente (N:N)

---

#### **modelo/producto_ingrediente.py**
```python
class ProductoIngrediente(SQLModel, table=True):
    __tablename__ = "producto_ingrediente"
    
    producto_id: Optional[int] = Field(
        default=None, 
        foreign_key="producto.id", 
        primary_key=True
    )
    ingrediente_id: Optional[int] = Field(
        default=None, 
        foreign_key="ingrediente.id", 
        primary_key=True
    )
    cantidad: float = Field(gt=0)
    
    # Relaciones bidireccionales
    producto: Optional["Producto"] = Relationship(back_populates="ingrediente_links")
    ingrediente: Optional["Ingrediente"] = Relationship(back_populates="producto_links")
```

**¿Qué es?**
- Tabla **pivot** (intermedia) para la relación N:N
- Almacena la cantidad de cada ingrediente por producto

**Campos:**
| Campo | Tipo | Validación |
|-------|------|-----------|
| `producto_id` | int | FK → producto.id, PK |
| `ingrediente_id` | int | FK → ingrediente.id, PK |
| `cantidad` | float | Mayor a 0 |

---

### 4️⃣ **schemas/** - Validación de Datos (Pydantic)

```python
from sqlmodel import SQLModel, Field

class CategoriaCreate(SQLModel):
    nombre: str = Field(min_length=2, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=200)

class IngredienteCreate(SQLModel):
    nombre: str = Field(min_length=2, max_length=50)
    unidad: str = Field(max_length=20)

class ProductoCreate(SQLModel):
    nombre: str = Field(min_length=2, max_length=100)
    precio: float = Field(gt=0)
    descripcion: Optional[str] = Field(default=None, max_length=300)
    categoria_id: Optional[int] = Field(default=None)
```

**¿Qué son?**
- Esquemas Pydantic para **validar datos de entrada**
- Aseguran que los datos cumplan restricciones antes de guardar
- Se usan principalmente en `POST` y `PUT`

**Diferencia Models vs Schemas:**
- **Models** → Representación en BD (con ID, timestamps, etc.)
- **Schemas** → Datos de entrada/salida en API (sin ID generalmente)

---

### 5️⃣ **routers/** - Endpoints HTTP (Controladores)

**¿Qué son?**
- Definen los **endpoints** (rutas) de la API
- Reciben requests HTTP
- Delegan lógica a **servicios**
- Retornan respuestas JSON

#### **routers/categorias.py - Ejemplo Completo**

```python
from fastapi import APIRouter, Depends, Query
from typing import Annotated, Optional
from sqlmodel import Session
from database import get_session
from models.categoria import Categoria
from services.categoria_service import CategoriaService

# Define el router con prefijo y tags
router = APIRouter(prefix="/categorias", tags=["categorias"])

# Tipo anotado para inyección de dependencia
SessionDep = Annotated[Session, Depends(get_session)]

def get_categoria_service(session: SessionDep) -> CategoriaService:
    """Crea y proporciona el servicio"""
    return CategoriaService(session)

CategoriaServiceDep = Annotated[CategoriaService, Depends(get_categoria_service)]

# ==================== ENDPOINTS ====================

@router.get("/", response_model=list[Categoria])
def get_categorias(
    service: CategoriaServiceDep,
    nombre: Annotated[Optional[str], Query(max_length=50)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10
):
    """GET /categorias - Obtiene lista de categorías"""
    return service.get_all(nombre, offset, limit)

@router.get("/{categoria_id}", response_model=Categoria)
def get_categoria(categoria_id: int, service: CategoriaServiceDep):
    """GET /categorias/1 - Obtiene una categoría por ID"""
    return service.get_by_id(categoria_id)

@router.post("/", response_model=Categoria, status_code=201)
def crear_categoria(categoria: Categoria, service: CategoriaServiceDep):
    """POST /categorias - Crea una nueva categoría"""
    return service.create(categoria)

@router.put("/{categoria_id}", response_model=Categoria)
def editar_categoria(categoria_id: int, datos: Categoria, service: CategoriaServiceDep):
    """PUT /categorias/1 - Actualiza una categoría"""
    return service.update(categoria_id, datos)

@router.delete("/{categoria_id}", status_code=204)
def eliminar_categoria(categoria_id: int, service: CategoriaServiceDep):
    """DELETE /categorias/1 - Elimina una categoría"""
    service.delete(categoria_id)
```

**Conceptos clave:**

| Concepto | Explicación |
|----------|-----------|
| `@router.get()` | Endpoint GET (lectura) |
| `@router.post()` | Endpoint POST (creación) |
| `@router.put()` | Endpoint PUT (actualización) |
| `@router.delete()` | Endpoint DELETE (eliminación) |
| `response_model=Categoria` | Valida respuesta con Pydantic |
| `Depends()` | Inyección de dependencias |
| `Query()` | Parámetro en query string (?nombre=x) |

---

### 6️⃣ **services/** - Lógica de Negocio

**¿Qué son?**
- Contienen la **lógica de negocio**
- Orquestan operaciones usando **repositories**
- Validan datos y manejan errores
- **Reutilizables** desde múltiples routers

#### **services/categoria_service.py - Ejemplo**

```python
from fastapi import HTTPException
from sqlmodel import Session
from models.categoria import Categoria
from uow import UnitOfWork

class CategoriaService:
    """Servicio de lógica de negocio para Categorías"""
    
    def __init__(self, session: Session):
        self.uow = UnitOfWork(session)  # Acceso a datos
    
    def get_all(self, nombre: str | None = None, offset: int = 0, limit: int = 10) -> list[Categoria]:
        """Obtiene categorías, opcionalmente filtradas por nombre"""
        if nombre:
            return self.uow.categorias.find_by_nombre(nombre)[offset:offset + limit]
        return self.uow.categorias.get_all(offset, limit)
    
    def get_by_id(self, categoria_id: int) -> Categoria:
        """Obtiene una categoría por ID, lanza error si no existe"""
        categoria = self.uow.categorias.get_by_id(categoria_id)
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoria no encontrada")
        return categoria
    
    def create(self, categoria: Categoria) -> Categoria:
        """Crea una nueva categoría"""
        categoria = self.uow.categorias.create(categoria)
        self.uow.commit()  # Confirma cambios en BD
        self.uow.session.refresh(categoria)  # Recarga para obtener ID auto-generado
        return categoria
    
    def update(self, categoria_id: int, datos: Categoria) -> Categoria:
        """Actualiza una categoría existente"""
        categoria = self.get_by_id(categoria_id)  # Verifica que exista
        categoria.nombre = datos.nombre
        categoria.descripcion = datos.descripcion
        categoria = self.uow.categorias.update(categoria)
        self.uow.commit()
        self.uow.session.refresh(categoria)
        return categoria
    
    def delete(self, categoria_id: int) -> None:
        """Elimina una categoría"""
        self.get_by_id(categoria_id)  # Verifica que exista
        self.uow.categorias.delete(categoria_id)
        self.uow.commit()
```

**Métodos:**

| Método | Entrada | Salida | ¿Qué hace? |
|--------|---------|--------|-----------|
| `get_all()` | nombre (opt), offset, limit | List[Categoria] | Lista con filtros |
| `get_by_id()` | categoria_id | Categoria | Obtiene 1, lanza error si no existe |
| `create()` | Categoria | Categoria | Crea y retorna con ID |
| `update()` | id, datos | Categoria | Actualiza y retorna |
| `delete()` | categoria_id | None | Elimina |

---

### 7️⃣ **uow/** - Unit of Work Pattern (Acceso a Datos)

**¿Qué es?**
- Patrón para gestionar **transacciones** y **repositorios**
- Centraliza todas las operaciones de BD
- Proporciona `commit()` y `rollback()`

#### **uow/repository.py - Clase Base Genérica**

```python
from typing import TypeVar, Generic, List, Optional
from sqlmodel import Session, select

T = TypeVar("T", bound=DeclarativeBase)

class BaseRepository(Generic[T]):
    """Repositorio base con operaciones CRUD comunes"""
    
    def __init__(self, session: Session, model: type[T]):
        self.session = session
        self.model = model
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Obtiene una entidad por ID"""
        return self.session.get(self.model, id)
    
    def get_all(self, offset: int = 0, limit: int = 10) -> List[T]:
        """Obtiene todas las entidades con paginación"""
        statement = select(self.model).offset(offset).limit(limit)
        return self.session.exec(statement).all()
    
    def create(self, obj: T) -> T:
        """Crea una nueva entidad"""
        self.session.add(obj)
        self.session.flush()
        return obj
    
    def update(self, obj: T) -> T:
        """Actualiza una entidad"""
        self.session.merge(obj)
        self.session.flush()
        return obj
    
    def delete(self, id: int) -> bool:
        """Elimina una entidad"""
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            self.session.flush()
            return True
        return False
```

**Métodos Genéricos:**

| Método | Funcionamiento |
|--------|--------|
| `get_by_id(id)` | `SELECT * FROM tabla WHERE id = ?` |
| `get_all(offset, limit)` | `SELECT * FROM tabla LIMIT ? OFFSET ?` |
| `create(obj)` | `INSERT INTO tabla VALUES (...)` |
| `update(obj)` | `UPDATE tabla SET ... WHERE id = ?` |
| `delete(id)` | `DELETE FROM tabla WHERE id = ?` |

---

#### **uow/categoria_repository.py - Heredado**

```python
from .repository import BaseRepository

class CategoriaRepository(BaseRepository[Categoria]):
    """Repositorio específico para Categoría"""
    
    def __init__(self, session: Session):
        super().__init__(session, Categoria)
    
    def find_by_nombre(self, nombre: str) -> List[Categoria]:
        """Búsqueda personalizada: por nombre (LIKE)"""
        statement = select(Categoria).where(Categoria.nombre.contains(nombre))
        return self.session.exec(statement).all()
```

**Hereda todos los CRUD de BaseRepository + métodos personalizados**

---

#### **uow/producto_repository.py - Más Métodos Personalizados**

```python
class ProductoRepository(BaseRepository[Producto]):
    
    def find_by_nombre(self, nombre: str) -> List[Producto]:
        """WHERE nombre LIKE '%nombre%'"""
        statement = select(Producto).where(Producto.nombre.contains(nombre))
        return self.session.exec(statement).all()
    
    def find_by_categoria(self, categoria_id: int, offset: int = 0, limit: int = 10) -> List[Producto]:
        """WHERE categoria_id = ?"""
        statement = select(Producto).where(Producto.categoria_id == categoria_id).offset(offset).limit(limit)
        return self.session.exec(statement).all()
    
    def find_by_nombre_y_categoria(self, nombre: str, categoria_id: int, offset: int = 0, limit: int = 10) -> List[Producto]:
        """WHERE nombre LIKE ? AND categoria_id = ?"""
        statement = select(Producto).where(
            Producto.nombre.contains(nombre),
            Producto.categoria_id == categoria_id
        ).offset(offset).limit(limit)
        return self.session.exec(statement).all()
```

---

#### **uow/unit_of_work.py - Gestor Centralizado**

```python
from sqlmodel import Session
from .categoria_repository import CategoriaRepository
from .ingrediente_repository import IngredienteRepository
from .producto_repository import ProductoRepository

class UnitOfWork:
    """Patrón Unit of Work: gestiona todos los repositorios y transacciones"""
    
    def __init__(self, session: Session):
        self.session = session
        # Instancia todos los repositorios
        self.categorias = CategoriaRepository(session)
        self.ingredientes = IngredienteRepository(session)
        self.productos = ProductoRepository(session)
    
    def commit(self):
        """Confirma todos los cambios en la BD"""
        self.session.commit()
    
    def rollback(self):
        """Revierte todos los cambios"""
        self.session.rollback()
    
    def close(self):
        """Cierra la sesión"""
        self.session.close()
```

**¿Por qué UnitOfWork?**
- ✅ Centraliza acceso a datos
- ✅ Gestiona transacciones (commit/rollback)
- ✅ Reutilizable en servicios
- ✅ Fácil de testear (mock un UnitOfWork en tests)

---

## Flujo de Ejecución

```
┌─────────────────────┐
│   Cliente HTTP      │
│  (Frontend/Postman) │
└──────────┬──────────┘
           │
           │ GET /categorias?nombre=bebidas
           │
           ▼
┌─────────────────────────────────────┐
│  routers/categorias.py              │
│  @router.get("/")                   │
│  def get_categorias(service: ...)   │
└──────────┬──────────────────────────┘
           │
           │ Llama service.get_all(nombre, offset, limit)
           │
           ▼
┌─────────────────────────────────────┐
│  services/categoria_service.py      │
│  def get_all(nombre, offset, limit) │
│  - Valida parámetros                │
│  - Maneja errores                   │
└──────────┬──────────────────────────┘
           │
           │ Usa self.uow.categorias.find_by_nombre(nombre)
           │
           ▼
┌──────────────────────────────────────┐
│  uow/categoria_repository.py         │
│  def find_by_nombre(nombre)          │
│  - Crea query SQL                    │
│  - Ejecuta en BD                     │
└──────────┬───────────────────────────┘
           │
           │ SELECT * FROM categoria WHERE nombre LIKE '%bebidas%'
           │
           ▼
┌──────────────────────────────────────┐
│  BD (PostgreSQL/MySQL/SQLite)        │
│  Retorna: [Bebidas, Bebidas Calientes]
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  Repository → Service → Router       │
│  Procesa respuesta                   │
│  Valida con Pydantic (response_model)
└──────────┬───────────────────────────┘
           │
           │ JSON Response
           │
           ▼
┌─────────────────────────────────────┐
│   Cliente HTTP                      │
│   [{"id": 1, "nombre": "Bebidas"}]  │
└─────────────────────────────────────┘
```

---

## Base de Datos

### Tablas Creadas

```
┌────────────────────────┐
│      CATEGORIA         │
├────────────────────────┤
│ id (PK)                │
│ nombre (str)           │
│ descripcion (str, opt) │
└────────────────────────┘
         │ 1:N
         │
┌────────────────────────┐
│      PRODUCTO          │
├────────────────────────┤
│ id (PK)                │
│ nombre (str)           │
│ precio (float)         │
│ descripcion (str, opt) │
│ categoria_id (FK)      │
└────────────────────────┘
         │ N:N
         │
┌───────────────────────────┐
│  PRODUCTO_INGREDIENTE     │
├───────────────────────────┤
│ producto_id (PK, FK)      │
│ ingrediente_id (PK, FK)   │
│ cantidad (float)          │
└───────────────────────────┘
         │ N:N
         │
┌────────────────────────┐
│    INGREDIENTE         │
├────────────────────────┤
│ id (PK)                │
│ nombre (str)           │
│ unidad (str)           │
└────────────────────────┘
```

---

## Cómo Usar la API

### Instalación

```bash
# Clonar/descargar proyecto
cd backend

# Crear venv
python -m venv .venv

# Activar venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env
DATABASE_URL=sqlite:///database.db  # o tu BD

# Ejecutar
uvicorn main:app --reload
```

### URL Base

```
http://localhost:8000
```

---

### Endpoints de Categorías

#### **GET** - Listar categorías
```bash
curl "http://localhost:8000/categorias?offset=0&limit=10"

# Con filtro por nombre
curl "http://localhost:8000/categorias?nombre=bebidas"
```

**Response:**
```json
[
  {
    "id": 1,
    "nombre": "Bebidas",
    "descripcion": "Bebidas en general"
  }
]
```

---

#### **GET** - Obtener una categoría
```bash
curl "http://localhost:8000/categorias/1"
```

**Response:**
```json
{
  "id": 1,
  "nombre": "Bebidas",
  "descripcion": "Bebidas en general"
}
```

---

#### **POST** - Crear categoría
```bash
curl -X POST "http://localhost:8000/categorias" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Postres",
    "descripcion": "Postres y dulces"
  }'
```

**Response:**
```json
{
  "id": 2,
  "nombre": "Postres",
  "descripcion": "Postres y dulces"
}
```

---

#### **PUT** - Actualizar categoría
```bash
curl -X PUT "http://localhost:8000/categorias/1" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Bebidas Frías",
    "descripcion": "Bebidas frías y refrescantes"
  }'
```

---

#### **DELETE** - Eliminar categoría
```bash
curl -X DELETE "http://localhost:8000/categorias/1"
```

**Response:** `204 No Content`

---

### Endpoints de Productos

#### **GET** - Listar productos
```bash
# Todos
curl "http://localhost:8000/productos?offset=0&limit=10"

# Por nombre
curl "http://localhost:8000/productos?nombre=coca"

# Por categoría
curl "http://localhost:8000/productos?categoria_id=1"

# Por nombre Y categoría
curl "http://localhost:8000/productos?nombre=coca&categoria_id=1"
```

---

#### **POST** - Crear producto
```bash
curl -X POST "http://localhost:8000/productos" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Coca Cola 2L",
    "precio": 3.50,
    "descripcion": "Botella de 2 litros",
    "categoria_id": 1
  }'
```

---

### Endpoints de Ingredientes

Similar a categorías y productos:

```bash
# Listar
curl "http://localhost:8000/ingredientes"

# Crear
curl -X POST "http://localhost:8000/ingredientes" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Azúcar",
    "unidad": "kg"
  }'
```

---

## Ejemplos de Código

### Ejemplo 1: Crear un Producto con Categoría

```python
# 1. Crear categoría
POST /categorias
{
  "nombre": "Bebidas",
  "descripcion": "Bebidas frías"
}
# Respuesta: id = 1

# 2. Crear producto
POST /productos
{
  "nombre": "Sprite 2L",
  "precio": 2.99,
  "descripcion": "Botella de 2 litros",
  "categoria_id": 1
}
# Respuesta: id = 1
```

---

### Ejemplo 2: Agregar Ingredientes a un Producto

```python
# 1. Crear ingrediente
POST /ingredientes
{
  "nombre": "Agua carbonatada",
  "unidad": "litros"
}

# 2. Crear relación (desde BD directamente)
INSERT INTO producto_ingrediente (producto_id, ingrediente_id, cantidad)
VALUES (1, 1, 2.0)  -- 2 litros de agua en producto ID 1
```

---

### Ejemplo 3: Buscar Productos por Categoría

```python
# Frontend hace request
GET /productos?categoria_id=1

# Backend:
# 1. Router recibe request
# 2. Inyecta ProductoService
# 3. Service llama repository.find_by_categoria(1)
# 4. Repository ejecuta SQL:
#    SELECT * FROM producto WHERE categoria_id = 1
# 5. Retorna lista de productos
```

---

## Agregar Nuevas Funcionalidades

### Pasos para Agregar una Nueva Entidad (ej: Usuario)

#### **Paso 1: Crear Modelo**
```python
# models/usuario.py
from sqlmodel import SQLModel, Field

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, max_length=100)
    nombre: str = Field(min_length=2, max_length=100)
    contraseña: str = Field(min_length=8)
```

#### **Paso 2: Crear Repository**
```python
# uow/usuario_repository.py
class UsuarioRepository(BaseRepository[Usuario]):
    def find_by_email(self, email: str) -> Optional[Usuario]:
        statement = select(Usuario).where(Usuario.email == email)
        return self.session.exec(statement).first()
```

#### **Paso 3: Agregar a UnitOfWork**
```python
# uow/unit_of_work.py
class UnitOfWork:
    def __init__(self, session: Session):
        # ... otros repositorios ...
        self.usuarios = UsuarioRepository(session)
```

#### **Paso 4: Crear Service**
```python
# services/usuario_service.py
class UsuarioService:
    def __init__(self, session):
        self.uow = UnitOfWork(session)
    
    def crear(self, usuario: Usuario) -> Usuario:
        # Validar email único, hashear contraseña, etc.
        usuario = self.uow.usuarios.create(usuario)
        self.uow.commit()
        return usuario
```

#### **Paso 5: Crear Router**
```python
# routers/usuarios.py
router = APIRouter(prefix="/usuarios", tags=["usuarios"])

@router.post("/", response_model=Usuario, status_code=201)
def crear_usuario(usuario: Usuario, service: UsuarioServiceDep):
    return service.crear(usuario)
```

#### **Paso 6: Incluir en main.py**
```python
from routers import usuarios
app.include_router(usuarios.router)
```

---

## Resumen

| Componente | Responsabilidad |
|-----------|-----------------|
| **main.py** | Configurar app, incluir routers |
| **database.py** | Conectar BD, proporcionar sesiones |
| **models/** | Definir estructuras (tablas) |
| **schemas/** | Validar datos de entrada/salida |
| **routers/** | Definir endpoints HTTP |
| **services/** | Lógica de negocio |
| **uow/** | Acceso a datos y transacciones |

---

**¡Tu API está lista para desarrollar! 🚀**

Para más info, consulta:
- 📄 `ARQUITECTURA.md` - Estructura modular
- 📊 `RELACIONES.md` - Diagrama de relaciones BD
