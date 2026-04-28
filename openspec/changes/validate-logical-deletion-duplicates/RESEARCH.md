## Research Analysis: Logical Deletion Duplicates Validation

### Soft-Delete Pattern Analysis

**Tables with Soft-Delete (activo: bool)**:
1. `Categoria` (models/categoria.py) - column: `activo: bool = Field(default=True)`
2. `Ingrediente` (models/ingrediente.py) - column: `activo: bool = Field(default=True)`
3. `Producto` (models/producto.py) - column: `activo: bool = Field(default=True)`

**Table without Soft-Delete**:
- `ProductoIngrediente` - no `activo` field (hard delete only)

**Naming Fields**: All use `nombre: str` (not `name`), so validation targets `nombre` column.

### Architecture Overview

**Stack**: FastAPI + SQLModel (SQLAlchemy) + Python

**Structure**:
- Models: SQLModel classes with relationships
- Repositories: `BaseRepository[T]` generic with soft-delete logic
- Services: Business logic layer (CategoriaService, ProductoService, IngredienteService)
- Routers: FastAPI endpoints
- UnitOfWork pattern: `UnitOfWork(session)` manages transactions

**Soft-Delete Implementation**:
- `BaseRepository.delete(id)` sets `activo = False` if model has `activo` field
- `BaseRepository.get_by_id()` and `get_all()` filter by `activo == True`
- All queries automatically exclude inactive records

### Error Handling Pattern

**Current Approach**:
- Services raise `HTTPException(status_code=404, detail="...")` for not found
- Uses Pydantic validation for input validation
- No custom exception classes yet

**Response Format**: FastAPI auto-converts HTTPException to JSON:
```json
{"detail": "error message"}
```

### Key Fields for Validation

**Categoria**:
- PK: `id` (int)
- Name: `nombre: str` (min 2, max 50)
- Soft-delete: `activo: bool`

**Ingrediente**:
- PK: `id` (int)
- Name: `nombre: str` (min 2, max 50)
- Soft-delete: `activo: bool`

**Producto**:
- PK: `id` (int)
- Name: `nombre: str` (min 2, max 100)
- Soft-delete: `activo: bool`

### Implementation Strategy

1. **Custom Exceptions** (new module: `exceptions.py`)
   - `DuplicateNameError` - base class
   - `DuplicateNameActiveError` - extends with `DUPLICATE_NAME_ACTIVE` code
   - `DuplicateNameInactiveError` - extends with `DUPLICATE_NAME_INACTIVE` code

2. **Validation Method** (extend `BaseRepository`)
   - `validate_nombre_uniqueness(nombre: str, exclude_id: Optional[int] = None)`
   - Checks ALL records (active + inactive) for duplicate names
   - Returns: (is_duplicate: bool, is_active: bool | None)
   - Raises appropriate exception if duplicate found

3. **Exception Handlers** (main.py or exception_handlers.py)
   - Map custom exceptions to HTTP 409 responses
   - Include error code and descriptive message

4. **Service Integration**
   - Call validation in `create()` and `update()` before persisting
   - Transaction wraps validation + save (atomicity)

5. **Database Indexes**
   - Add index on `nombre` for each table
   - Use Alembic migrations (if present) or raw SQL script

### Notes

- No need for unique constraint on `nombre` (soft-deletes must allow duplicates in inactive state temporarily)
- Validation logic lives in repository layer (DDD approach)
- Error messages in Spanish (project convention)
- HTTP 409 Conflict is correct response for name collisions
