## 1. Implementar validación en PaginaProductos

- [x] 1.1 Crear función `handleNuevoProducto()` que valida `categorias.length > 0`
- [x] 1.2 Si no hay categorías, llamar `showToast('warning', 'Debes crear al menos una categoría antes')`
- [x] 1.3 Si hay categorías, ejecutar `resetForm()` y `setShowModal(true)`
- [x] 1.4 Reemplazar onClick del botón "+ Nuevo" para usar `handleNuevoProducto` en lugar del inline lambda

## 2. Verificación y testing manual

- [ ] 2.1 Verificar que cuando no hay categorías, clickear "+ Nuevo" muestra el toast
- [ ] 2.2 Verificar que el modal NO se abre cuando no hay categorías
- [ ] 2.3 Crear una categoría desde la página de Categorías
- [ ] 2.4 Volver a Productos y verificar que "+ Nuevo" abre el modal normalmente
- [ ] 2.5 Verificar que el formulario carga las categorías en el dropdown

## 3. Validación de edge cases

- [ ] 3.1 Eliminar la categoría desde Categorías y volver a Productos
- [ ] 3.2 Verificar que "+ Nuevo" vuelve a mostrar el toast
- [ ] 3.3 Verificar que la consola del navegador no muestra errores

