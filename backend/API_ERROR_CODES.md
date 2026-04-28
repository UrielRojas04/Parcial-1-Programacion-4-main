# Documentación API: Validación de Nombres Duplicados

## Error HTTP 409 Conflict - Nombres Duplicados

### Descripción
Cuando intentas crear o actualizar un elemento con un nombre que ya existe (activo o inactivo), el sistema retorna HTTP 409 Conflict.

### Respuesta HTTP 409 - Formato

```json
{
  "detail": "Mensaje de error descriptivo",
  "error_code": "DUPLICATE_NAME_ACTIVE o DUPLICATE_NAME_INACTIVE",
  "nombre": "El nombre que causó el conflicto"
}
```

---

## Códigos de Error Específicos

### DUPLICATE_NAME_ACTIVE

**Descripción**: El nombre ya está en uso por un elemento activo.

**Mensaje**: `"El nombre '{nombre}' ya está en uso."`

**Causa**: Existe otro elemento CON EL MISMO NOMBRE que está activo.

**Acción del Cliente**:
1. Elige un nombre diferente
2. O espera a que el elemento existente sea desactivado
3. O contacta al administrador si el nombre es crítico

**Ejemplo**:
```bash
POST /categorias
{
  "nombre": "Bebidas",
  "descripcion": "Bebidas varias"
}
```

**Respuesta (409)**:
```json
{
  "detail": "El nombre 'Bebidas' ya está en uso.",
  "error_code": "DUPLICATE_NAME_ACTIVE",
  "nombre": "Bebidas"
}
```

---

### DUPLICATE_NAME_INACTIVE

**Descripción**: El nombre está en uso por un elemento desactivado (soft-deleted).

**Mensaje**: `"El nombre '{nombre}' ya está en uso (inactivo). Por favor, comuníquese con el administrador para resolver este conflicto."`

**Causa**: Existe un elemento con el mismo nombre que fue desactivado (soft-deleted) pero su nombre aún está "reservado".

**Acción del Cliente**:
1. Contactar al administrador del sistema
2. El administrador debe resolver el conflicto (ver ADMIN_GUIDE.md)
3. El administrador puede:
   - Renombrar el elemento inactivo
   - Eliminar físicamente el elemento (purga)
   - Fusionar datos

**Ejemplo**:
```bash
POST /productos
{
  "nombre": "Pizza Napolitana",
  "precio": 250.0
}
```

**Respuesta (409)**:
```json
{
  "detail": "El nombre 'Pizza Napolitana' ya está en uso (inactivo). Por favor, comuníquese con el administrador para resolver este conflicto.",
  "error_code": "DUPLICATE_NAME_INACTIVE",
  "nombre": "Pizza Napolitana"
}
```

---

## Operaciones Afectadas

### POST (CREATE)

**Endpoint**: `POST /{entidad}`

**Validación**: Verifica que el nombre NO exista (activo o inactivo)

**Códigos posibles**:
- `201 Created` - Éxito
- `409 Conflict` - Nombre duplicado
- `422 Unprocessable Entity` - Validación de entrada (nombre muy corto, etc.)

**Ejemplo de Error**:
```bash
curl -X POST http://localhost:8000/ingredientes \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Harina", "unidad": "kg"}'

# Error (409) si "Harina" ya existe
```

---

### PUT (UPDATE)

**Endpoint**: `PUT /{entidad}/{id}`

**Validación**: Verifica que el nombre NO exista EN OTROS ELEMENTOS (activos o inactivos)

**Códigos posibles**:
- `200 OK` - Éxito
- `404 Not Found` - Elemento no existe
- `409 Conflict` - Nombre duplicado en otro elemento
- `422 Unprocessable Entity` - Validación de entrada

**Nota**: Puedes actualizar un elemento al MISMO nombre (no es error)

**Ejemplo**:
```bash
# Scenario 1: Renombrar a nombre disponible (OK)
curl -X PUT http://localhost:8000/categorias/1 \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Nuevas Bebidas"}'
# Response: 200 OK

# Scenario 2: Renombrar a nombre duplicado (409)
curl -X PUT http://localhost:8000/categorias/1 \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Alimentos"}' # si "Alimentos" ya existe
# Response: 409 Conflict
```

---

## DELETE (Soft Delete)

**Endpoint**: `DELETE /{entidad}/{id}`

**Comportamiento**: 
- Marca el elemento como `activo = false` (soft-delete)
- El nombre queda "reservado" para futuro
- Nadie puede crear/actualizar a ese nombre

**Códigos**:
- `204 No Content` - Éxito (soft-deleted)
- `404 Not Found` - Elemento no existe

**Nota**: El soft-delete NO lanza 409 porque el nombre NO se libera; pasa a estado "inactivo".

---

## GET (Lectura)

**Comportamiento**: 
- Los GET siempre retornan solo elementos ACTIVOS
- Los elementos con `activo = false` NO aparecen en listados
- Si intentas GET un elemento con ID que está inactivo, retorna 404

```bash
# Elemento activo: disponible
GET /categorias/1
# Response: 200 OK (categoria.activo == true)

# Elemento inactivo: no encontrado
GET /categorias/1
# Response: 404 Not Found (categoria.activo == false)
```

---

## Manejo de Errores en el Cliente

### Pseudocódigo (JavaScript/TypeScript)

```javascript
async function createProducto(data) {
  try {
    const response = await fetch('/productos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (response.status === 409) {
      const error = await response.json();
      
      if (error.error_code === 'DUPLICATE_NAME_ACTIVE') {
        showErrorUI(`El nombre "${error.nombre}" ya está en uso. Elige otro.`);
        suggestAlternativeNames(error.nombre);
      } 
      else if (error.error_code === 'DUPLICATE_NAME_INACTIVE') {
        showErrorUI(`El nombre "${error.nombre}" está reservado. Contacta al administrador.`);
        showContactAdminButton();
      }
    } 
    else if (!response.ok) {
      throw new Error(await response.text());
    }
    
    return await response.json();
  } catch (err) {
    console.error('Error:', err);
  }
}
```

---

## Tabla Resumen

| Escenario | Método | Status | error_code | Acción |
|-----------|--------|--------|-----------|--------|
| Crear con nombre único | POST | 201 | - | Éxito |
| Crear con nombre duplicado activo | POST | 409 | DUPLICATE_NAME_ACTIVE | Elige otro nombre |
| Crear con nombre duplicado inactivo | POST | 409 | DUPLICATE_NAME_INACTIVE | Contacta admin |
| Actualizar a nombre único | PUT | 200 | - | Éxito |
| Actualizar a nombre duplicado activo | PUT | 409 | DUPLICATE_NAME_ACTIVE | Elige otro nombre |
| Actualizar a nombre duplicado inactivo | PUT | 409 | DUPLICATE_NAME_INACTIVE | Contacta admin |
| Actualizar al MISMO nombre | PUT | 200 | - | Éxito (sin cambio) |
| Desactivar elemento | DELETE | 204 | - | Éxito (nombre se reserva) |

---

## Ejemplos Completos

### Flujo: Crear Categoría

```bash
# Paso 1: Crea categoría "Bebidas"
$ curl -X POST http://localhost:8000/categorias \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Bebidas", "descripcion": "Bebidas frías"}'

# Response: 201 Created
{
  "id": 1,
  "nombre": "Bebidas",
  "descripcion": "Bebidas frías",
  "activo": true,
  "parent_id": null
}

# Paso 2: Intenta crear otra "Bebidas" (FAIL - activa)
$ curl -X POST http://localhost:8000/categorias \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Bebidas", "descripcion": "Otra bebida"}'

# Response: 409 Conflict
{
  "detail": "El nombre 'Bebidas' ya está en uso.",
  "error_code": "DUPLICATE_NAME_ACTIVE",
  "nombre": "Bebidas"
}

# Paso 3: Desactiva la original
$ curl -X DELETE http://localhost:8000/categorias/1

# Response: 204 No Content (sin body)

# Paso 4: Intenta crear "Bebidas" nuevamente (FAIL - inactiva)
$ curl -X POST http://localhost:8000/categorias \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Bebidas", "descripcion": "Nueva bebida"}'

# Response: 409 Conflict
{
  "detail": "El nombre 'Bebidas' ya está en uso (inactivo). Por favor, comuníquese con el administrador para resolver este conflicto.",
  "error_code": "DUPLICATE_NAME_INACTIVE",
  "nombre": "Bebidas"
}

# Paso 5: Crear con nombre diferente (OK)
$ curl -X POST http://localhost:8000/categorias \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Bebidas Premium", "descripcion": "Nueva categoría"}'

# Response: 201 Created
{
  "id": 2,
  "nombre": "Bebidas Premium",
  "descripcion": "Nueva categoría",
  "activo": true,
  "parent_id": null
}
```

---

## Notas Importantes

1. **Sensibilidad de Casos**: La validación es case-SENSITIVE
   - "Harina" ≠ "harina"
   - Si necesitas case-insensitive, actualiza `validate_nombre_uniqueness` en `repository.py`

2. **Espacios en Blanco**: Se preservan tal cual
   - "Harina  " (dos espacios) ≠ "Harina " (un espacio)

3. **Caracteres Especiales**: Se permiten todos
   - "Harina & Trigo" es válido
   - "Harina/Integral" es válido

4. **Largo de Nombres**:
   - Categoria: 2-50 caracteres
   - Ingrediente: 2-50 caracteres
   - Producto: 2-100 caracteres

5. **Transaccionalidad**: 
   - La validación ocurre DENTRO de la transacción
   - Si hay error, se rollback automático
   - No quedan datos parciales en la BD
