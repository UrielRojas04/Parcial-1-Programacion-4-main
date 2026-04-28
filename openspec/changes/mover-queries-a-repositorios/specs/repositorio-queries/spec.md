## ADDED Requirements

### Requirement: Queries centralizadas en repositorios
El sistema DEBE concentrar todas las queries SQL/SQLModel en repositorios específicos dentro de `uow/` y NO permitir queries directas en services.

#### Scenario: Query personalizada definida en repositorio
- **WHEN** un service necesita una consulta específica (ej. conteo por categoría)
- **THEN** existe un método en el repositorio correspondiente que implementa la query y el service lo invoca
