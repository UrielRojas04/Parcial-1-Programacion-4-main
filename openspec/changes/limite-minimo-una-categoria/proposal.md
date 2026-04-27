## Why

Los usuarios deben poder crear productos en la aplicación, pero sin categorías disponibles, la experiencia es confusa: el modal se abre con un dropdown vacío. La restricción de negocio es clara: **un producto debe tener siempre una categoría disponible** (aunque puede crearse sin asignarla explícitamente). Para mantener la integridad de datos y evitar estados inválidos, bloqueamos la apertura del formulario de creación de productos cuando no existen categorías.

## What Changes

- **Frontend**: Al hacer click en "+ Nuevo Producto", se verifica que exista al menos una categoría en el sistema.
  - Si existen categorías: el modal se abre normalmente.
  - Si NO existen categorías: muestra un toast de advertencia ("Debes crear al menos una categoría antes") y **no abre el modal**.
- **User Flow**: Se previene que el usuario intente crear un producto sin categorías disponibles, mejorando la UX al no mostrar un formulario incompleto.

## Capabilities

### New Capabilities

- `producto-require-categoria`: Validación en frontend que impide abrir el modal de creación de productos si no existe al menos una categoría en el sistema.

### Modified Capabilities

<!-- No existing requirements change. This is a new validation constraint. -->

## Impact

- **Frontend (React)**: `src/pages/PaginaProductos.tsx`
  - Nueva función `handleNuevoProducto()` que verifica `categorias.length > 0` antes de abrir el modal.
  - Toast de advertencia usando contexto existente `ToastContext`.
- **UX**: El botón "+ Nuevo Producto" bloquea flujo si no hay categorías.
- **Backend**: Sin cambios. La validación es únicamente en frontend.
- **APIs**: Sin cambios en endpoints.
