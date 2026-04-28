## Context

Actualmente hay queries SQL/SQLModel definidas dentro de services (ej.: `select(...)` en `categoria_service.py`). Esto acopla la lógica de negocio con persistencia y obliga a tests con BD o mocks de sesión. Ya existe capa de repositorios en `uow/`, pero no concentra todas las consultas personalizadas.

## Goals / Non-Goals

**Goals:**
- Consolidar todas las queries en repositorios (`uow/*_repository.py`).
- Dejar services como orquestadores de reglas de negocio sin SQL/SQLModel directo.
- Mantener el comportamiento actual de los endpoints (sin cambios contractuales).

**Non-Goals:**
- No se modifican modelos, esquemas ni endpoints.
- No se agrega infraestructura nueva (ORM distinto, cache, etc.).
- No se reestructura todo el Unit of Work.

## Decisions

- **Mover queries al repositorio específico por entidad.**
  - Alternativas: (a) dejar queries en services, (b) crear un repositorio "query" común. Se elige (a) repositorio específico porque mantiene cohesión y reduce acoplamiento.
- **Services solo invocan métodos de repositorio.**
  - Alternativa: usar `session.exec` directo en services. Se descarta por mezcla de responsabilidades.
- **Mantener nombres de métodos orientados al dominio.**
  - Ej.: `contar_productos_por_categoria(categoria_id)` en `CategoriaRepository`.

## Risks / Trade-offs

- **Riesgo:** duplicación de lógica si hay consultas similares en varios repositorios → **Mitigación:** crear métodos reutilizables en el repositorio base si aplica.
- **Riesgo:** olvidar mover alguna query puntual → **Mitigación:** revisar services buscando `select(` o `session.exec`.
