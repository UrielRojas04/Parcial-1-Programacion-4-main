# Guía para Ejecutar Tests de Validación de Nombres Duplicados

## Requisitos Previos

```bash
pip install pytest sqlmodel sqlalchemy
```

## Ejecutar Tests Unitarios

### Todos los tests
```bash
cd backend
python -m pytest tests/test_nombre_validation.py -v
```

### Tests específicos por entidad
```bash
# Solo tests de Categoría
python -m pytest tests/test_nombre_validation.py::TestCategoriaValidation -v

# Solo tests de Ingrediente
python -m pytest tests/test_nombre_validation.py::TestIngredienteValidation -v

# Solo tests de Producto
python -m pytest tests/test_nombre_validation.py::TestProductoValidation -v
```

### Tests específicos
```bash
# Test de crear categoría con nombre duplicado activo
python -m pytest tests/test_nombre_validation.py::TestCategoriaValidation::test_crear_categoria_duplicada_activa_lanza_excepcion -v
```

## Resultados Esperados

✓ 11 tests should pass:

1. `test_crear_categoria_nombre_unico` - Crear categoría con nombre único
2. `test_crear_categoria_duplicada_activa_lanza_excepcion` - Rechaza duplicate activo
3. `test_crear_categoria_duplicada_inactiva_lanza_excepcion` - Rechaza duplicate inactivo
4. `test_actualizar_categoria_nombre_unico` - Actualizar a nombre único
5. `test_actualizar_categoria_a_nombre_duplicado_lanza_excepcion` - Rechaza update a duplicate
6. `test_crear_ingrediente_nombre_unico` - Crear ingrediente único
7. `test_crear_ingrediente_duplicado_activo_lanza_excepcion` - Rechaza duplicate activo
8. `test_crear_ingrediente_duplicado_inactivo_lanza_excepcion` - Rechaza duplicate inactivo
9. `test_crear_producto_nombre_unico` - Crear producto único
10. `test_crear_producto_duplicado_activo_lanza_excepcion` - Rechaza duplicate activo
11. `test_crear_producto_duplicado_inactivo_lanza_excepcion` - Rechaza duplicate inactivo

## Ejecutar Tests de API (E2E)

### Crear categoría con nombre duplicado (debe retornar 409)
```bash
# Terminal 1: Inicia el servidor
uvicorn main:app --reload

# Terminal 2: Crea primera categoría
curl -X POST http://localhost:8000/categorias \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Bebidas", "descripcion": "test"}'

# Response: 201 Created
# {"id": 1, "nombre": "Bebidas", "descripcion": "test", "activo": true}

# Intenta crear duplicada
curl -X POST http://localhost:8000/categorias \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Bebidas", "descripcion": "otro"}'

# Response: 409 Conflict
# {
#   "detail": "El nombre 'Bebidas' ya está en uso.",
#   "error_code": "DUPLICATE_NAME_ACTIVE",
#   "nombre": "Bebidas"
# }
```

### Crear categoría con nombre de inactiva (debe retornar 409 con mensaje especial)
```bash
# Desactiva la categoría
curl -X DELETE http://localhost:8000/categorias/1 -H "Content-Type: application/json"

# Intenta crear con el mismo nombre
curl -X POST http://localhost:8000/categorias \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Bebidas", "descripcion": "nueva"}'

# Response: 409 Conflict
# {
#   "detail": "El nombre 'Bebidas' ya está en uso (inactivo). Por favor, comuníquese con el administrador para resolver este conflicto.",
#   "error_code": "DUPLICATE_NAME_INACTIVE",
#   "nombre": "Bebidas"
# }
```

## Verificar Índices en la Base de Datos

### SQLite
```bash
sqlite3 database.db
# Una vez dentro de sqlite3:
.tables
PRAGMA index_list(categoria);
PRAGMA index_list(ingrediente);
PRAGMA index_list(producto);
```

Expected output:
```
idx_categoria_nombre
idx_ingrediente_nombre
idx_producto_nombre
```

## Notas de Testing

- Los tests usan una BD en memoria (no afectan la BD real)
- Cada test es independiente con su propia sesión de BD
- Los fixtures de pytest crean y limpian la BD automáticamente
- Para debugging, usa `-s` flag: `pytest -v -s test_nombre_validation.py`
