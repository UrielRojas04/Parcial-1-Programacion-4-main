# Estrategia de Deployment y Monitoreo

## Visión General

Este documento describe cómo desplegar la validación de nombres duplicados de forma segura y cómo monitorear su funcionamiento en producción.

---

## Fase 1: Pre-Deployment (1-2 días antes)

### Checklist

- [ ] Tests unitarios pasan 100% (`pytest tests/test_nombre_validation.py`)
- [ ] Tests de integración pasan 100% (`pytest tests/test_api_validation.py`)
- [ ] Índices de BD creados y verificados
- [ ] Documentación actualizada (API_ERROR_CODES.md, ADMIN_GUIDE.md)
- [ ] Equipo de soporte capacitado
- [ ] Plan de rollback disponible
- [ ] Monitoreo configurado

### Capacitación del Equipo

**Para Desarrolladores**:
- Revisar DEVELOPER_GUIDE.md
- Conocer cómo aplicar validación a nuevas entidades
- Entender que `validate_nombre_uniqueness()` es genérico

**Para Soporte/Administradores**:
- Revisar ADMIN_GUIDE.md
- Entender códigos de error: ACTIVE vs INACTIVE
- Conocer los 3 enfoques de resolución
- Preparar templates de respuesta a usuarios

**Para QA**:
- Ejecutar tests de API completamente
- Verificar respuestas en cada entidad (Categoria, Ingrediente, Producto)
- Probar casos edge (nombres con espacios, caracteres especiales)

---

## Fase 2: Deployment (Día del Lanzamiento)

### Opción A: Sin Feature Flag (Recomendado para equipos pequeños)

**Paso 1**: Backup de datos
```bash
# Antes de desplegar
tar -czf database_$(date +%s).tar.gz database.db
```

**Paso 2**: Deploy de código
```bash
# En tu CI/CD o local
git pull origin main
pip install -r requirements.txt
# o si usas Docker:
docker-compose up --build backend -d
```

**Paso 3**: Aplicar migraciones de índices
```bash
cd backend
python migrations/apply_indexes.py
```

**Paso 4**: Reiniciar servicio
```bash
# Si es systemd:
sudo systemctl restart nombre-app

# Si es Docker:
docker-compose restart backend

# Si es local dev:
# Solo detén y reinicia el uvicorn
```

**Paso 5**: Verificación
```bash
# Verifica que el servicio esté arriba
curl http://localhost:8000/

# Intenta crear un elemento
curl -X POST http://localhost:8000/categorias \
  -H "Content-Type: application/json" \
  -d '{"nombre": "TestCategory", "descripcion": "test"}'
```

### Opción B: Con Feature Flag (Recomendado para grandes equipos)

**Implementación** (si quieres ser más conservador):

1. Agrega variable de environment:
```python
# En main.py o config.py
import os
ENABLE_DUPLICATE_NAME_VALIDATION = os.getenv("ENABLE_DUPLICATE_NAME_VALIDATION", "true").lower() == "true"
```

2. Modifica BaseRepository:
```python
def validate_nombre_uniqueness(self, nombre: str, exclude_id: Optional[int] = None):
    if not ENABLE_DUPLICATE_NAME_VALIDATION:
        return False, None  # Skip validation if disabled
    # ... resto de lógica
```

3. Deploy sin activar:
```bash
# Deploy con flag desactivado inicialmente
export ENABLE_DUPLICATE_NAME_VALIDATION=false
docker-compose up backend -d
```

4. Monitoreo 24h sin validación
5. Activar gradualmente:
```bash
# Después de 24h sin problemas
export ENABLE_DUPLICATE_NAME_VALIDATION=true
docker-compose up backend -d
```

---

## Fase 3: Post-Deployment (48 horas críticas)

### Monitoreo Continuo

**Hora 0-2**: Monitor Activo
- [ ] Revisar logs cada 15 minutos
- [ ] Verificar que no hay errores inesperados
- [ ] Confirmar que usuarios reciben errores 409 correctamente

**Hora 2-12**: Monitor Moderado
- [ ] Revisar logs cada hora
- [ ] Buscar patrones de duplicados frecuentes
- [ ] Verificar performance (queries de validación)

**Hora 12-48**: Monitor Estándar
- [ ] Revisar logs cada 4 horas
- [ ] Analizar métricas acumuladas
- [ ] Preparar reporte para stakeholders

### Qué Buscar en Logs

**Indicadores de ÉXITO**:
```
[DUPLICATE_NAME_ACTIVE] requests → Usuario intentó reutilizar nombre → Retornó 409 → Usuario recibió error claro
[DUPLICATE_NAME_INACTIVE] requests → Usuario intentó reutilizar nombre inactivo → Retornó 409 con mensaje admin
```

**Indicadores de PROBLEMA**:
```
- Thousands of 409s en 1 hora → Posible bug o mala UX
- 0 validations en 48h → Posible que validación no esté activa
- Errores de DB connection → Índices no se crearon o BD corrupta
- Performance degradation → Índices no están siendo usados
```

### Consultas de Monitoreo

```bash
# Contar intentos fallidos por tipo (en servidor)
grep "DUPLICATE_NAME" logs/duplicate_name_events.log | wc -l

# Ver últimos 10 intentos
tail -10 logs/duplicate_name_events.log

# Ver attempts en última hora
grep "$(date +%H)" logs/duplicate_name_events.log

# Contar por tipo
grep "DUPLICATE_NAME_ACTIVE" logs/duplicate_name_events.log | wc -l
grep "DUPLICATE_NAME_INACTIVE" logs/duplicate_name_events.log | wc -l
```

### Endpoint de Métricas (si implementaste)

```bash
curl http://localhost:8000/admin/metrics/duplicate-names \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Response:
# {
#   "DUPLICATE_NAME_ACTIVE": 42,
#   "DUPLICATE_NAME_INACTIVE": 3
# }
```

---

## Fase 4: Rollback (Si es necesario)

### Rollback Plan

**Opción 1**: Desactivar Feature Flag (Menos invasivo)
```bash
export ENABLE_DUPLICATE_NAME_VALIDATION=false
docker-compose restart backend
# Continúa investigando sin afectar usuarios
```

**Opción 2**: Revert Completo (Si hay bug crítico)
```bash
# Revert código
git revert <commit_hash>

# Revert migraciones (solo si falla)
# DROP INDEX idx_categoria_nombre, idx_ingrediente_nombre, idx_producto_nombre;

# Redeploy
docker-compose up --build backend -d
```

**Estimado de tiempo**: 5-15 minutos con downtime mínimo

---

## Fase 5: Post-Incident (Si ocurrió problema)

### RCA (Root Cause Analysis)

**Pasos**:
1. ¿Cuándo empezó el problema?
2. ¿Qué logs hay alrededor de ese momento?
3. ¿Cambió algo en la BD (tamaño, estado)?
4. ¿Cambió algo en el código recientemente?
5. ¿Hay pattern en los usuarios afectados?

### Mejoras Implementadas

Después de resolver, agrega al código:
- [ ] Mejor logging del problema
- [ ] Monitoreo preventivo
- [ ] Test que capture el edge case
- [ ] Documentación de gotcha

---

## Runbook para Administradores

### Situación: "Usuarios reportan 409 al crear elementos"

**Paso 1**: Verificar que es error esperado
```bash
# Ver logs
tail -f logs/duplicate_name_events.log

# Busca líneas con DUPLICATE_NAME_ACTIVE
# Si ves muchas, es normal. Si son pocas, es un edge case.
```

**Paso 2**: Contactar al usuario
```
Estimado usuario,

Recibimos tu solicitud de crear "{nombre}". 

Disculpa, ese nombre ya está en uso en el sistema. 
Por favor, elige un nombre diferente.

Si crees que esto es un error, contacta al equipo de soporte.

Atentamente,
Sistema
```

---

### Situación: "Usuario reporta 409 INACTIVE"

**Paso 1**: Investigar
```bash
# Verifica que el elemento inactivo existe
sqlite3 database.db
SELECT * FROM categoria WHERE nombre = 'Bebidas' AND activo = false;
```

**Paso 2**: Escolher estrategia (ver ADMIN_GUIDE.md)
- Opción 1: Renombrar inactivo
- Opción 2: Fusionar datos
- Opción 3: Purgar

**Paso 3**: Ejecutar resolución

**Paso 4**: Confirmar al usuario
```
Estimado usuario,

Hemos resuelto el conflicto de nombre. 
Ya puedes crear "{nombre}" sin problemas.

Gracias por tu paciencia.
```

---

### Situación: "Validación no está funcionando"

**Diagnóstico**:
```bash
# 1. ¿El servicio está arriba?
curl http://localhost:8000/ 

# 2. ¿El feature flag está activo?
echo $ENABLE_DUPLICATE_NAME_VALIDATION

# 3. ¿Los índices existen?
sqlite3 database.db ".indices"

# 4. ¿Los cambios de código están deployados?
grep "validate_nombre_uniqueness" backend/uow/categoria_repository.py
```

**Fix**:
```bash
# Si feature flag está off:
export ENABLE_DUPLICATE_NAME_VALIDATION=true

# Si índices faltan:
cd backend && python migrations/apply_indexes.py

# Si código no está actualizado:
git pull && python migrations/apply_indexes.py && docker-compose restart backend
```

---

## Monitoreo a Largo Plazo (Semanas 2+)

### Métricas Semanales

```
- Total de intentos fallidos
- Ratio de ACTIVE vs INACTIVE
- Elementos inactivos que bloquean nombres
- Performance de queries (ms)
- Storage impact de índices
```

### Reporte Semanal

Enviar a stakeholders cada lunes:

```markdown
## Reporte: Validación de Nombres Duplicados

**Semana**: Oct 24 - Oct 30

### Métricas
- Intentos fallidos: 137 (ACTIVE: 130, INACTIVE: 7)
- Entidades más afectadas: Productos (80%), Categorías (15%), Ingredientes (5%)
- Tiempo de respuesta: <5ms (normal)

### Alertas
- 7 conflictos INACTIVE requieren revisión del admin
- 1 usuario con 20+ intentos (posible bug en app cliente?)

### Acciones
- [ ] Revisar usuario con 20+ intentos
- [ ] Resolver 7 conflictos INACTIVE
- [ ] Actualizar FAQ con casos más frecuentes
```

---

## Healthcheck

Agrega este endpoint para monitoreo automático:

```python
@app.get("/healthz")
def healthz():
    return {
        "status": "ok",
        "validation_active": ENABLE_DUPLICATE_NAME_VALIDATION,
        "metrics": DuplicateNameLogger.get_metrics()
    }
```

Monitorea con:
```bash
# Cada 5 minutos
*/5 * * * * curl -f http://localhost:8000/healthz || alert_ops
```

---

## Checklist Final Pre-Production

- [ ] Tests: 100% pass
- [ ] Índices: Creados y verificados
- [ ] Logging: Configurado y testado
- [ ] Monitoreo: Dashboards listos
- [ ] Documentación: Actualizada
- [ ] Equipo: Capacitado
- [ ] Backup: Realizado
- [ ] Rollback: Plan listo
- [ ] Communication: Usuarios notificados (si corresponde)
- [ ] Feature flag: Disponible (si aplica)

**Go Live Aprobado**: ✓
