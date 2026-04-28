# Guía del Desarrollador: Patrón de Validación de Nombres Duplicados

## Visión General

Este documento explica cómo se implementa la validación de nombres duplicados y cómo aplicarla a nuevas entidades en el proyecto.

---

## Arquitectura

### Componentes

```
┌─────────────────────────────────────────┐
│ Router (routers/categorias.py)          │
│ - Recibe POST/PUT requests              │
│ - Valida input básico (Pydantic)        │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ Service (services/categoria_service.py) │
│ - Lógica de negocio                     │
│ - Llama a repository.create/update      │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ Repository (uow/categoria_repository.py)│
│ - create() llama validate_nombre_...()  │ ◄─ VALIDACIÓN AQUÍ
│ - update() llama validate_nombre_...()  │
│ - Lanza DuplicateNameError si hay dupe  │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ BaseRepository.validate_nombre_...()    │ ◄─ MÉTODO GENÉRICO
│ - Busca nombre en BD (all records)      │
│ - Distingue activo vs inactivo          │
│ - Lanza excepción apropiada             │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│ FastAPI Exception Handler (main.py)     │
│ - Captura DuplicateNameError            │
│ - Convierte a HTTP 409 JSON response    │
└─────────────────────────────────────────┘
```

---

## Implementación Paso a Paso

### Paso 1: Modelo (Model)

El modelo DEBE tener:
1. Columna `nombre: str`
2. Columna `activo: bool` (para soft-delete)
3. Decorador `table=True` en SQLModel

**Ejemplo** (`models/categoria.py`):
```python
from sqlmodel import SQLModel, Field

class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=2, max_length=50)  # ◄ Requerido
    descripcion: Optional[str] = None
    activo: bool = Field(default=True)  # ◄ Requerido
```

---

### Paso 2: Repositorio Específico

Extiende `BaseRepository` y SOBRESCRIBE `create()` y `update()`:

```python
from .repository import BaseRepository
from models.categoria import Categoria

class CategoriaRepository(BaseRepository[Categoria]):
    def __init__(self, session: Session):
        super().__init__(session, Categoria)
    
    def create(self, obj: Categoria) -> Categoria:
        """Crea validando unicidad de nombre"""
        self.validate_nombre_uniqueness(obj.nombre)  # ◄ VALIDACIÓN
        return super().create(obj)
    
    def update(self, obj: Categoria) -> Categoria:
        """Actualiza validando unicidad (excluyendo el ID actual)"""
        self.validate_nombre_uniqueness(obj.nombre, exclude_id=obj.id)  # ◄ VALIDACIÓN
        return super().update(obj)
```

**Puntos Clave**:
- `validate_nombre_uniqueness(nombre)` para CREATE
- `validate_nombre_uniqueness(nombre, exclude_id=obj.id)` para UPDATE
- Esto asegura que el UPDATE al mismo nombre no falla
- El método lanza excepciones automáticamente

---

### Paso 3: Servicio (Service)

Los servicios llaman al repositorio sin cambios específicos (la validación ya ocurre):

```python
class CategoriaService:
    def __init__(self, session: Session):
        self.uow = UnitOfWork(session)
    
    def create(self, categoria: Categoria) -> Categoria:
        with self.uow:
            # Repository.create() ya valida nombre
            new_cat = self.uow.categorias.create(categoria)
            self.uow.session.refresh(new_cat)
            return new_cat
    
    def update(self, categoria_id: int, datos: Categoria) -> Categoria:
        with self.uow:
            # Repository.update() ya valida nombre
            categoria = self.uow.categorias.update(datos)
            self.uow.session.refresh(categoria)
            return categoria
```

**Nota**: La excepción `DuplicateNameError` se propaga automáticamente hasta FastAPI, donde el handler la convierte a HTTP 409.

---

### Paso 4: Handler de Excepciones (ya existe en main.py)

El handler YA está configurado en `main.py`:

```python
from exceptions import DuplicateNameError

@app.exception_handler(DuplicateNameError)
async def duplicate_name_exception_handler(request: Request, exc: DuplicateNameError):
    return JSONResponse(
        status_code=409,
        content={
            "detail": exc.message,
            "error_code": exc.error_code.value,
            "nombre": exc.nombre,
        },
    )
```

**No necesita cambios** para nuevas entidades. El handler es genérico.

---

## Aplicar a Nueva Entidad

Para agregar validación de nombres duplicados a una entidad nueva:

### Checklist

- [ ] **Modelo**: Tiene campos `nombre: str` y `activo: bool`
- [ ] **Repositorio**: Extiende `BaseRepository` y sobrescribe `create()` y `update()`
  - [ ] `create()` llama `self.validate_nombre_uniqueness(obj.nombre)`
  - [ ] `update()` llama `self.validate_nombre_uniqueness(obj.nombre, exclude_id=obj.id)`
- [ ] **Servicio**: Usa el repositorio (sin cambios específicos)
- [ ] **Test**: Escribe tests unitarios en `tests/test_nombre_validation.py`
- [ ] **Índice BD**: Agrega índice en `migrations/001_add_name_indexes.sql`

### Ejemplo Completo: Nueva Entidad "Proveedor"

**1. Modelo** (`models/proveedor.py`):
```python
from sqlmodel import SQLModel, Field
from typing import Optional

class Proveedor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=2, max_length=100)  # ◄ Requerido
    email: str
    activo: bool = Field(default=True)  # ◄ Requerido
```

**2. Repositorio** (`uow/proveedor_repository.py`):
```python
from .repository import BaseRepository
from models.proveedor import Proveedor

class ProveedorRepository(BaseRepository[Proveedor]):
    def __init__(self, session: Session):
        super().__init__(session, Proveedor)
    
    def create(self, obj: Proveedor) -> Proveedor:
        self.validate_nombre_uniqueness(obj.nombre)
        return super().create(obj)
    
    def update(self, obj: Proveedor) -> Proveedor:
        self.validate_nombre_uniqueness(obj.nombre, exclude_id=obj.id)
        return super().update(obj)
```

**3. Unit of Work** (`uow/unit_of_work.py`):
```python
# Agrega al __init__:
from .proveedor_repository import ProveedorRepository

class UnitOfWork:
    def __init__(self, session: Session):
        self.proveedores = ProveedorRepository(session)  # ◄ Agrega esta línea
        # ... otros repos
```

**4. Índice en BD** (`migrations/001_add_name_indexes.sql`):
```sql
CREATE INDEX IF NOT EXISTS idx_proveedor_nombre ON proveedor(nombre);
```

**5. Test** (agrega a `tests/test_nombre_validation.py`):
```python
class TestProveedorValidation:
    def test_crear_proveedor_nombre_unico(self, session: Session):
        repo = ProveedorRepository(session)
        prov = Proveedor(nombre="Acme Inc", email="acme@example.com")
        result = repo.create(prov)
        assert result.nombre == "Acme Inc"
    
    def test_crear_proveedor_duplicado_lanza_excepcion(self, session: Session):
        repo = ProveedorRepository(session)
        prov1 = Proveedor(nombre="Acme Inc", email="a@a.com")
        repo.create(prov1)
        
        prov2 = Proveedor(nombre="Acme Inc", email="b@b.com")
        with pytest.raises(DuplicateNameActiveError):
            repo.create(prov2)
```

---

## Detalles de Implementación

### BaseRepository.validate_nombre_uniqueness()

**Firma**:
```python
def validate_nombre_uniqueness(
    self, 
    nombre: str, 
    exclude_id: Optional[int] = None
) -> Tuple[bool, Optional[bool]]:
```

**Parámetros**:
- `nombre`: String a validar
- `exclude_id`: ID de la entidad a excluir de la búsqueda (para UPDATE)

**Comportamiento**:
1. Busca `nombre` en TODOS los registros (activos e inactivos)
2. Si excluye un ID, no lo cuenta
3. Si encuentra duplicado:
   - Si está activo → Lanza `DuplicateNameActiveError`
   - Si está inactivo → Lanza `DuplicateNameInactiveError`
4. Si no hay duplicado → Retorna `(False, None)`

**Nota**: El método LANZA EXCEPCIONES, no retorna valores. El retorno es por si lo necesitas en lógica futura.

---

## Troubleshooting

### Problema: "validate_nombre_uniqueness not found"

**Causa**: Olvidaste heredar de `BaseRepository` o no llamaste a `super().__init__()`

**Solución**:
```python
class MiRepository(BaseRepository[MiEntidad]):  # ◄ Hereda de BaseRepository
    def __init__(self, session: Session):
        super().__init__(session, MiEntidad)  # ◄ Llama super().__init__()
```

---

### Problema: "Validación no se ejecuta"

**Causa**: No sobrescribiste `create()` o `update()` en tu repositorio

**Solución**: Asegúrate de que llames a `self.validate_nombre_uniqueness()`:
```python
def create(self, obj: MiEntidad) -> MiEntidad:
    self.validate_nombre_uniqueness(obj.nombre)  # ◄ AÑADE ESTA LÍNEA
    return super().create(obj)
```

---

### Problema: "ExcludeID no funciona en UPDATE"

**Causa**: Pasaste `exclude_id=None` o la entidad no tiene `id` asignado

**Solución**:
```python
# Asegúrate de que obj.id exista:
def update(self, obj: MiEntidad) -> MiEntidad:
    assert obj.id is not None, "Entity must have ID for update"
    self.validate_nombre_uniqueness(obj.nombre, exclude_id=obj.id)
    return super().update(obj)
```

---

### Problema: Índices no se crean

**Causa**: Migraciones no se ejecutaron

**Solución**: 
```bash
# Desde el directorio backend:
python migrations/apply_indexes.py
```

---

## Consideraciones de Rendimiento

### Índices
- Agrega índice en `nombre` para todas las entidades
- Esto mejora la búsqueda de duplicados de O(n) a O(log n)

### Caché (Futuro)
- Si tienes muchas búsquedas de nombres, considera Redis
- Implementa en `validate_nombre_uniqueness()` después si es necesario

### Transactions
- La validación ocurre DENTRO de la transacción `with self.uow:`
- Si falla validación, se rollback automático
- No hay datos parciales en la BD

---

## Testing

### Estructura Recomendada

```python
class TestNuevEntidad:
    def test_crear_nombre_unico(self, session):
        """Happy path"""
    
    def test_crear_duplicado_activo(self, session):
        """Falla con excepción correcta"""
    
    def test_crear_duplicado_inactivo(self, session):
        """Falla con excepción correcta"""
    
    def test_actualizar_nombre_unico(self, session):
        """Happy path"""
    
    def test_actualizar_a_duplicado(self, session):
        """Falla correctamente"""
```

---

## Logging (Opcional)

Para loguear intentos fallidos:

```python
from logging_config import log_duplicate_name_on_create, log_duplicate_name_on_update

class MiRepository(BaseRepository[MiEntidad]):
    def create(self, obj: MiEntidad) -> MiEntidad:
        try:
            self.validate_nombre_uniqueness(obj.nombre)
        except DuplicateNameError as e:
            log_duplicate_name_on_create(e, "MiEntidad")  # ◄ Log
            raise
        return super().create(obj)
```

---

## Referencias

- **Excepciones**: `backend/exceptions.py`
- **BaseRepository**: `backend/uow/repository.py`
- **Ejemplos**: `backend/uow/categoria_repository.py`, `backend/uow/ingrediente_repository.py`
- **Tests**: `backend/tests/test_nombre_validation.py`
- **Documentación Admin**: `backend/ADMIN_GUIDE.md`
- **Documentación API**: `backend/API_ERROR_CODES.md`
