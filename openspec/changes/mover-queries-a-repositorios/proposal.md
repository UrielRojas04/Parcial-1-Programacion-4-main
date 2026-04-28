## Why

Hoy las queries viven en los services (por ejemplo, `select(...)` en `categoria_service.py`). Eso mezcla lógica de negocio con acceso a datos, complica los tests, y rompe la separación de responsabilidades. Mover las queries a los repositorios reduce el acoplamiento y hace más mantenible el backend.

## What Changes

- Centralizar las queries SQL/SQLModel en repositorios específicos (`uow/*_repository.py`).
- Dejar en los services solo reglas de negocio y orquestación.
- Exponer nuevos métodos en repositorios para las consultas personalizadas.
- Actualizar services para usar esos métodos y no construir queries.

## Capabilities

### New Capabilities
- `repositorio-queries`: Reglas y puntos únicos de acceso a datos (queries) desde repositorios.

### Modified Capabilities
- `servicios-sin-queries`: Los services ya no crean queries directas; delegan en repositorios.

## Impact

- Afecta `services/*.py` y `uow/*_repository.py`.
- No cambia endpoints ni contratos HTTP.
- Tests unitarios se simplifican al mockear repositorios.
