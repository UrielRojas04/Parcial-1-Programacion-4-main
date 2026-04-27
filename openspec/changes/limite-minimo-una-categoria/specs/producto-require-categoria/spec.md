## ADDED Requirements

### Requirement: Validar existencia de categorías antes de crear producto

El sistema SHALL validar que exista al menos una categoría en el sistema antes de permitir que el usuario abra el formulario de creación de un nuevo producto. Si no existen categorías, SHALL mostrar un mensaje de advertencia y NO DEBE abrir el modal de creación.

#### Scenario: Usuario intenta crear producto sin categorías existentes
- **WHEN** el usuario hace click en "+ Nuevo Producto" y no hay categorías en el sistema
- **THEN** el sistema muestra un toast de tipo 'warning' con el mensaje "Debes crear al menos una categoría antes"
- **AND** el modal de creación de producto NO se abre
- **AND** el usuario permanece en la misma página

#### Scenario: Usuario intenta crear producto con categorías existentes
- **WHEN** el usuario hace click en "+ Nuevo Producto" y existen categorías en el sistema
- **THEN** el sistema abre el modal de creación de producto
- **AND** el formulario muestra el dropdown de categorías con opciones disponibles
- **AND** el usuario puede llenar el formulario y crear el producto

#### Scenario: Las categorías se cargan después de que el usuario ve la página
- **WHEN** el usuario está en la página de Productos (inicialmente sin categorías)
- **AND** el sistema carga categorías desde la API
- **THEN** el estado `categorias` se actualiza con las categorías cargadas
- **AND** el botón "+ Nuevo Producto" funciona normalmente (sin toast)

#### Scenario: El estado de categorías se vacía después de agregar una
- **WHEN** el usuario crea una categoría
- **AND** luego navega a otra página y regresa (forzando recarga)
- **AND** se elimina la categoría creada
- **THEN** intentar crear un nuevo producto muestra el toast de advertencia nuevamente

