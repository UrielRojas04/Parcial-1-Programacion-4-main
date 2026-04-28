## 1. Relevamiento de queries en services

- [x] 1.1 Buscar en `services/` usos de `select(`, `session.exec` o equivalentes
- [x] 1.2 Listar por entidad las consultas personalizadas a mover

## 2. Repositorios con queries

- [x] 2.1 Crear/actualizar métodos en `uow/*_repository.py` para cada consulta listada
- [x] 2.2 Asegurar nombres de métodos orientados al dominio (ej. `contar_productos_por_categoria`)

## 3. Refactor de services

- [x] 3.1 Reemplazar en services las queries directas por llamadas a repositorio
- [x] 3.2 Verificar que no queden imports de `select`/`func` innecesarios

## 4. Verificación rápida

- [x] 4.1 Revisar que todos los services cumplan “sin queries directas”
