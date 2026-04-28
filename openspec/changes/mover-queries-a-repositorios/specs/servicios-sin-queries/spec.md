## ADDED Requirements

### Requirement: Services sin acceso directo a SQL/SQLModel
Los services NO DEBEN construir ni ejecutar queries SQL/SQLModel de forma directa; deben delegar el acceso a datos en repositorios.

#### Scenario: Service consulta datos sin usar session.exec
- **WHEN** un service necesita leer datos
- **THEN** invoca un método del repositorio y NO usa `session.exec`, `select` ni APIs equivalentes
