# Guía para Administradores: Gestión de Conflictos de Nombres Duplicados

## Visión General

Cuando se desactiva un elemento (soft-delete), su nombre queda "reservado". El sistema no permite crear nuevos elementos con ese nombre, incluso si el anterior está inactivo. Esto asegura que no haya ambigüedad en los datos históricos.

## Códigos de Error

### DUPLICATE_NAME_ACTIVE
**Significado**: El nombre ya está en uso por un elemento activo.

**Respuesta HTTP**: 409 Conflict

**Mensaje**:
```
El nombre '{nombre}' ya está en uso.
```

**Acción**: El usuario debe elegir un nombre diferente o esperar a que el elemento con ese nombre sea desactivado.

---

### DUPLICATE_NAME_INACTIVE
**Significado**: El nombre está en uso por un elemento desactivado (soft-deleted).

**Respuesta HTTP**: 409 Conflict

**Mensaje**:
```
El nombre '{nombre}' ya está en uso (inactivo). 
Por favor, comuníquese con el administrador para resolver este conflicto.
```

**Acción**: Se requiere intervención del administrador. El sistema no permite automatizar la resolución porque hay múltiples enfoques válidos.

---

## Opciones de Resolución para DUPLICATE_NAME_INACTIVE

### Opción 1: Renombrar el Elemento Inactivo
**Escenario**: El usuario quiere reutilizar el nombre original.

**Pasos**:
1. Activa el elemento inactivo temporalmente (si es permitido)
2. Cambia su nombre a algo más descriptivo (ej: `"{nombre}_viejo"` o `"{nombre}_archivado"`)
3. Lo desactiva nuevamente
4. El usuario ahora puede crear/usar el nombre original

**Ventajas**:
- Preserva historial completo
- Clara trazabilidad de cambios
- El nombre se reutiliza completamente

**Desventajas**:
- Requiere manipulación manual
- Puede afectar reportes históricos

---

### Opción 2: Permitir Sobrescritura (Fusión)
**Escenario**: Fusionar datos del elemento inactivo con el nuevo.

**Pasos**:
1. Reactivar el elemento inactivo
2. Migrar/fusionar datos relacionados
3. Desactivarlo con los datos actualizados
4. Crear el nuevo elemento

**Ventajas**:
- Preserva datos relacionados
- Evita pérdida de información

**Desventajas**:
- Requiere lógica específica por entidad
- Complejo de automatizar

---

### Opción 3: Purga (Eliminación Física)
**Escenario**: El elemento inactivo no tiene valor y puede descartarse.

**Pasos**:
1. Verificar que no haya referencias importantes
2. Ejecutar DELETE directo en la base de datos (no soft-delete)
3. El nombre queda disponible

**Ventajas**:
- Simple y limpio
- Libera el nombre inmediatamente

**Desventajas**:
- Pérdida permanente de datos
- No recomendado para auditoría

---

## Monitoreo

### Logs Estructurados

**Ubicación**: `backend/logs/duplicate_name_events.log`

**Formato**:
```
2024-04-27 14:30:15 - WARNING - [DUPLICATE_NAME_ACTIVE] Categoria.create(nombre=Bebidas, id=None, user=admin@example.com)
2024-04-27 14:31:22 - WARNING - [DUPLICATE_NAME_INACTIVE] Producto.update(nombre=Pizza, id=5, user=chef@example.com)
```

### Métricas

Usa el módulo `logging_config.py` para obtener métricas en tiempo real:

```python
from logging_config import DuplicateNameLogger

metrics = DuplicateNameLogger.get_metrics()
print(metrics)
# {"DUPLICATE_NAME_ACTIVE": 12, "DUPLICATE_NAME_INACTIVE": 3}
```

### Endpoint de Monitoreo (Recomendado)

Agrega este endpoint al router de admin:

```python
@app.get("/admin/metrics/duplicate-names")
def get_duplicate_name_metrics(current_user: User = Depends(get_admin)):
    return DuplicateNameLogger.get_metrics()
```

---

## Dashboard de Administrador (Recomendado)

### Información a Mostrar

1. **Elementos Inactivos Bloqueando Nombres**
   - Query: `SELECT * FROM {tabla} WHERE activo = false ORDER BY nombre`
   - Mostrar: nombre, tipo, fecha de inactivación, usuario que lo inactivó

2. **Conflictos Recientes**
   - Query: `SELECT * FROM duplicate_name_events.log WHERE timestamp > NOW() - INTERVAL 7 DAY`
   - Mostrar: error_code, nombre, entity_type, acción, usuario

3. **Estadísticas**
   - Total de elementos inactivos por tipo
   - Intentos fallidos por semana
   - Elementos más frecuentemente duplicados

---

## Procedimiento Recomendado

### Cuando un Usuario Reporta "Nombre en Uso (inactivo)"

1. **Validar el Reporte**
   ```bash
   # Verifica que el elemento inactivo existe
   SELECT * FROM {tabla} WHERE nombre = ? AND activo = false
   ```

2. **Determinar la Causa**
   - ¿El usuario quiere reutilizar el nombre?
   - ¿El elemento inactivo tiene valor histórico?
   - ¿Hay datos relacionados?

3. **Elegir Opción de Resolución**
   - Si es histórico importante → Opción 1 (renombrar)
   - Si hay fusión posible → Opción 2 (fusionar)
   - Si no tiene valor → Opción 3 (purgar)

4. **Ejecutar Resolución**
   - Documentar el cambio
   - Registrar quién lo resolvió y por qué
   - Notificar al usuario

5. **Verificar**
   ```bash
   # Confirma que el nombre está disponible
   SELECT COUNT(*) FROM {tabla} WHERE nombre = ?
   # Debe retornar 0
   ```

---

## Ejemplos de Resolución en SQL

### Renombrar Elemento Inactivo
```sql
-- Rename inactive categoria
UPDATE categoria 
SET nombre = nombre || '_archivado' 
WHERE activo = false AND nombre = 'Bebidas';

-- Verify
SELECT nombre, activo FROM categoria WHERE nombre LIKE '%archivado%';
```

### Purgar Elemento Inactivo
```sql
-- Warning: Permanent deletion!
DELETE FROM categoria 
WHERE activo = false AND nombre = 'Bebidas';

-- Verify name is free
SELECT COUNT(*) FROM categoria WHERE nombre = 'Bebidas';
```

---

## Mejores Prácticas

1. **Nunca permitas automatización de purgas**
   - Siempre requiere confirmación del admin
   - Documentar razón de eliminación

2. **Mantén historial de resoluciones**
   - Crear tabla `admin_actions_log` si no existe
   - Registrar qué resolución se usó y por qué

3. **Revisa periódicamente elementos inactivos**
   - Identifica "zombies" que bloquean nombres
   - Limpia archivos que no tienen valor

4. **Comunica con usuarios**
   - Explica por qué existe esta restricción
   - Ofrece opciones claras

5. **Monitorea tendencias**
   - Si hay muchos conflictos INACTIVE, puede haber un patrón de mal uso
   - Ajusta procesos según sea necesario
