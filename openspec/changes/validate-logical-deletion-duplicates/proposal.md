## Why

Actualmente, cuando se desactiva lógicamente un elemento (soft delete), el sistema permite crear un nuevo elemento con el mismo nombre. Esto genera conflictos de datos y confusión en la integridad de la información. Es necesario validar que no exista un nombre duplicado activo o desactivado para evitar ambigüedades y mantener la consistencia de los datos.

## What Changes

- El sistema validará durante la creación de elementos que no exista otro elemento con el mismo nombre, independientemente de su estado (activo o desactivado)
- Si existe un conflicto, se retornará un error específico que informe al usuario que el nombre ya existe (desactivado)
- Se agregará un mensaje claro que recomiende contactar al administrador para resolver duplicados
- Las transacciones de validación ocurrirán a nivel de base de datos y aplicación

## Capabilities

### New Capabilities
- `logical-deletion-name-validation`: Validación de nombres únicos considerando elementos desactivados (soft deleted) en las tablas de base de datos

### Modified Capabilities
<!-- Ninguna capacidad existente cambia en sus requisitos, solo se agrega nueva lógica de validación -->

## Impact

- **Affected Code**: Capa de persistencia/repositorio, validadores de entidades
- **Affected Tables**: Todas las tablas que implementan soft delete (campos `is_active`, `deleted_at`, etc.)
- **API Impact**: Endpoints POST/PUT que crean o modifican elementos retornarán nuevos códigos de error específicos
- **Dependencies**: No se agregan dependencias externas; usa características existentes de la BD
