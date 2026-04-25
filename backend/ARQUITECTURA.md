# Estructura del Proyecto - Documentación

## Resumen

Tu proyecto ahora sigue una arquitectura modular bien organizada con separación de responsabilidades:

```
backend/
├── main.py                 # Punto de entrada de la aplicación
├── database.py            # Configuración de la BD y sesiones
├── requirements.txt       # Dependencias del proyecto
│
├── models/                # Definición de entidades
│   ├── __init__.py
│   ├── categoria.py
│   ├── ingrediente.py
│   ├── producto.py
│   └── producto_ingrediente.py
│
├── schemas/               # Esquemas de validación (Pydantic/SQLModel)
│   ├── __init__.py
│   └── schemas.py
│
├── routers/               # Endpoints de la API (controladores)
│   ├── __init__.py
│   ├── categorias.py
│   ├── ingredientes.py
│   └── productos.py
│
├── services/              # Lógica de negocio
│   ├── __init__.py
│   ├── categoria_service.py
│   ├── ingrediente_service.py
│   └── producto_service.py
│
└── uow/                   # Unit of Work Pattern (repositorios y transacciones)
    ├── __init__.py
    ├── repository.py           # Clase base con operaciones CRUD
    ├── categoria_repository.py
    ├── ingrediente_repository.py
    ├── producto_repository.py
    └── unit_of_work.py        # Gestor de transacciones y repositorios
```

---

## Componentes

### 1. **Models** (`models/`)
Definen la estructura de las entidades en la base de datos:
- `Categoria`, `Ingrediente`, `Producto`
- Incluyen validaciones a nivel de modelo

### 2. **Schemas** (`schemas/`)
Esquemas para validación de datos en requests/responses:
- `CategoriaCreate`, `IngredienteCreate`, `ProductoCreate`
- Utilizan validadores de Pydantic/SQLModel

### 3. **Routers** (`routers/`)
Endpoints de la API REST:
- Reciben requests HTTP
- Inyectan el servicio correspondiente
- Retornan respuestas formateadas
- **No contienen lógica de negocio**

```python
# Ejemplo: Router simple
@router.get("/")
def get_categorias(service: CategoriaServiceDep):
    return service.get_all()
```

### 4. **Services** (`services/`)
Contiene la lógica de negocio:
- `CategoriaService`, `IngredienteService`, `ProductoService`
- Orquestan operaciones de BD mediante el UnitOfWork
- Manejan validaciones y errores (HTTPException)
- Son reutilizables desde cualquier capa

```python
# Ejemplo: Service
class CategoriaService:
    def get_by_id(self, categoria_id: int) -> Categoria:
        categoria = self.uow.categorias.get_by_id(categoria_id)
        if not categoria:
            raise HTTPException(status_code=404, detail="No encontrada")
        return categoria
```

### 5. **UnitOfWork** (`uow/`)

#### `BaseRepository` (repository.py)
Clase base genérica con operaciones CRUD:
```python
get_by_id(id)
get_all(offset, limit)
create(obj)
update(obj)
delete(id)
```

#### Repositorios específicos
- `CategoriaRepository`, `IngredienteRepository`, `ProductoRepository`
- Heredan de `BaseRepository`
- Pueden tener métodos personalizados de búsqueda

```python
class CategoriaRepository(BaseRepository[Categoria]):
    def find_by_nombre(self, nombre: str) -> List[Categoria]:
        # búsqueda personalizada
```

#### `UnitOfWork` (unit_of_work.py)
Patrón que centraliza todos los repositorios y gestiona transacciones:
```python
class UnitOfWork:
    def __init__(self, session: Session):
        self.categorias = CategoriaRepository(session)
        self.ingredientes = IngredienteRepository(session)
        self.productos = ProductoRepository(session)
    
    def commit(self):
        self.session.commit()
    
    def rollback(self):
        self.session.rollback()
```

---

## Flujo de Ejecución

```
Cliente HTTP (Request)
    ↓
Router (routers/categorias.py)
    ↓
Service Dependency Injection (categorias_service.py)
    ↓
CategoriaService (lógica de negocio)
    ↓
UnitOfWork (uow/unit_of_work.py)
    ↓
Repositories (uow/categoria_repository.py)
    ↓
Base Repository (uow/repository.py)
    ↓
SQLModel/SQLAlchemy (acceso a BD)
    ↓
Respuesta HTTP (JSON)
```

---

## Ventajas de esta Arquitectura

✅ **Separación de responsabilidades**: Cada capa tiene un único propósito
✅ **Testeable**: Services y repositories pueden mockearse fácilmente
✅ **Reutilizable**: Services pueden usarse desde múltiples routers
✅ **Mantenible**: Cambios en BD afectan solo a repositories
✅ **Escalable**: Fácil agregar nuevas entidades (copy-paste)
✅ **Patrón Unit of Work**: Gestión centralizada de transacciones

---

## Cómo Agregar una Nueva Entidad

Si necesitas agregar una nueva entidad (ej: `Usuario`):

1. **Crear modelo**: `models/usuario.py`
   ```python
   class Usuario(SQLModel, table=True):
       id: Optional[int] = Field(default=None, primary_key=True)
       nombre: str
   ```

2. **Crear repositorio**: `uow/usuario_repository.py`
   ```python
   class UsuarioRepository(BaseRepository[Usuario]):
       # métodos personalizados
   ```

3. **Agregar a UnitOfWork**: `uow/unit_of_work.py`
   ```python
   self.usuarios = UsuarioRepository(session)
   ```

4. **Crear service**: `services/usuario_service.py`
   ```python
   class UsuarioService:
       def __init__(self, session):
           self.uow = UnitOfWork(session)
       # métodos de negocio
   ```

5. **Crear router**: `routers/usuarios.py`
   ```python
   @router.get("/")
   def get_usuarios(service: UsuarioServiceDep):
       return service.get_all()
   ```

6. **Incluir en main.py**:
   ```python
   from routers import usuarios
   app.include_router(usuarios.router)
   ```

---

## Testing

Ahora es fácil escribir tests unitarios:

```python
# test_categoria_service.py
from unittest.mock import Mock
from services.categoria_service import CategoriaService

def test_get_categoria():
    mock_session = Mock()
    service = CategoriaService(mock_session)
    # test
```

---

¡Tu proyecto está ahora organizado y listo para crecer! 🚀
