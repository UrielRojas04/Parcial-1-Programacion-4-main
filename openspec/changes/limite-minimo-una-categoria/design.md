## Context

Actualmente, el componente `PaginaProductos` carga categorías en un `useEffect` y las almacena en estado local. Cuando el usuario clickea "+ Nuevo", se abre un modal que permite crear un producto con o sin categoría. La experiencia es confusa si no hay categorías: el dropdown está vacío y no hay feedback visual de por qué el flujo no tiene sentido.

El estado actual:
- `categorias: Categoria[]` se inicializa vacío `[]`
- Se carga asincronicamente en `useEffect`
- El botón "+ Nuevo" abre el modal **incondicionalmente**
- No hay barrera de entrada

## Goals / Non-Goals

**Goals:**
- Bloquear la apertura del modal si `categorias.length === 0`
- Mostrar un toast informativo ("Debes crear al menos una categoría antes")
- Mantener la experiencia fluida si hay categorías (sin cambios)
- Usar infraestructura existente (ToastContext, Modal, etc.)

**Non-Goals:**
- No navegar automáticamente a Categorías (usuario decide)
- No agregar validación en backend (es decisión frontend)
- No cambiar el flujo de edición (solo afecta creación)
- No crear nuevas componentes o contextos

## Decisions

### Decisión 1: Punto de validación (Click handler)

**Opción A (Elegida)**: Validar en `handleNuevoProducto()` antes de abrir modal
```
User click → handleNuevoProducto() → if (categorias.length === 0) → toast + return
```

**Opción B (Descartada)**: Validar en el render (deshabilitar botón)
```
<button disabled={categorias.length === 0}>+ Nuevo</button>
```

**Rationale**: 
- A es mejor UX: botón siempre habilitado, pero con feedback inmediato (toast)
- Evita "ghost" buttons (deshabilitados sin razón aparente)
- El toast comunica la acción (es por falta de categorías)

---

### Decisión 2: Tipo de toast

**Opción A (Elegida)**: `'warning'`
- Tono: preventivo, no es error del usuario
- Visual: amarillo/naranja (destaca pero no alarmante)

**Opción B (Descartada)**: `'error'`
- Implicaría que algo salió mal (confunde)
- Rojo sería demasiado negativo

**Opción C (Descartada)**: `'info'`
- Muy neutral, podría pasar desapercibido

**Rationale**: `'warning'` comunica "necesitas esto primero" sin ser alarmista

---

### Decisión 3: Tiempo de check

**Opción A (Elegida)**: Chequear al click (estado actual de `categorias`)
```typescript
const handleNuevoProducto = () => {
  if (categorias.length === 0) { /* actúa */ }
}
```

**Opción B (Descartada)**: Chequear al montar o en API
- Innecesario (ya se carga en `useEffect`)
- Más complejo

**Rationale**: El estado ya está sincronizado cuando el usuario clickea

---

### Decisión 4: Implementación de la función

**Opción A (Elegida)**: Nueva función nombrada `handleNuevoProducto()`
```typescript
const handleNuevoProducto = () => {
  if (categorias.length === 0) {
    showToast('warning', 'Debes crear al menos una categoría antes');
    return;
  }
  resetForm();
  setShowModal(true);
};
```

**Opción B (Descartada)**: Inline en onClick
```typescript
onClick={() => {
  if (categorias.length === 0) { ... }
  else { ... }
}}
```

**Rationale**: Función nombrada es más legible, más fácil de testear y mantener

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| API falla cargando categorías → estado queda `[]` → user ve toast (podría ser confuso) | Low priority: error de API, no de lógica. Toast es correcto "no hay categorías" |
| User crea categoría en otra pestaña (concurrencia) → state no se sincroniza | Low: solo aplica si tienen pestañas del mismo navegador abiertas simultáneamente |
| Modal todavía tiene categorías vacías si se abre manualmente (edge case) | N/A: solo se abre a través del botón propuesto |

Trade-off: La lógica está en el click handler, no en el render, así que el estado siempre es evaluado en el momento de la acción (más correcto, menos optimizaciones posibles pero no importa para este caso).

