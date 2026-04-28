# GUIÓN DEL VIDEO ACTUALIZADO — PRIMER PARCIAL
## Programación IV — UTN

**Grupo:** Fabrizio Castillo · Uriel Rojas · Manuel Planero · Agustín Gérmenes · Joaquín Luna  
**Stack:** FastAPI + SQLModel + PostgreSQL + React + TypeScript + TanStack Query

---

## 📋 Distribución del Video

| Integrante | Sección | Tiempo |
|---|---|---|
| Joaquín | Intro + Ecosistema del Proyecto | ~3 min |
| Agustín | Modelado: Relaciones, Jerarquías y Validación | ~3 min |
| Fabrizio | Routers, Validaciones Declarativas y Excepciones | ~3 min |
| Manuel | Lógica de Negocio: Servicios y Reglas | ~3 min |
| Uriel | Unit of Work, Repositorios y Demo en Vivo | ~3 min |
| **TOTAL** | | **~15 min** |

---

## 🎬 SECCIÓN 1 — INTRO Y ECOSISTEMA DEL PROYECTO
### 🎤 Joaquín Luna | Intro + Ecosistema del Proyecto | ⏱ ~3 min

**[Pantalla: IDE abierto con la estructura del proyecto visible]**

VOZ:

"Hola, somos el grupo conformado por Fabrizio Castillo, Uriel Rojas, Manuel Planero, Agustín Gérmenes y Joaquín Luna, y hoy presentamos nuestro proyecto integrador de Programación IV.

Desarrollamos una aplicación Fullstack completa: un backend robusto construido con FastAPI y un frontend reactivo con React y TypeScript. El sistema es un gestor de productos gastronómicos que permite administrar categorías, ingredientes y productos, con relaciones complejas entre ellos.

La arquitectura del backend sigue un patrón de capas bien definida, donde cada capa tiene una única responsabilidad. Esto garantiza un código profesional, ordenado y mantenible.

**[Mostrar estructura del backend en el IDE: carpeta `backend/`]**

La estructura está organizada así:

• **models/** — Aquí definimos nuestras entidades de base de datos usando SQLModel, incluyendo las relaciones entre ellos.

• **schemas/** — Separamos deliberadamente los modelos de BD de los esquemas de entrada y salida. Pydantic valida los datos automáticamente.

• **routers/** — Los endpoints HTTP están declarados aquí. Cada router es responsable de una entidad.

• **services/** — La lógica de negocio reside acá, completamente desacoplada de los routers. Un servicio coordina operaciones y reglas.

• **uow/** — Implementación del patrón Unit of Work con repositorios genéricos para el acceso a datos, asegurando transacciones atómicas.

• **database.py** — Configuración centralizada de la base de datos y la sesión de SQLModel.

El punto de entrada es **main.py**, donde configuramos middlewares y handlers de excepciones personalizadas.

Todo esto demuestra cómo se construye una API profesional donde la lógica no está mezclada con los endpoints, sino organizada en capas claramente separadas. Agustín va a profundizar en cómo modelamos nuestras entidades y sus relaciones."

---

## 🎬 SECCIÓN 2 — MODELADO: RELACIONES, JERARQUÍAS Y VALIDACIÓN
### 🎤 Agustín Gérmenes | Modelado: Relaciones, Jerarquías y Validación | ⏱ ~3 min

**[Abrir `backend/models/` en el IDE. Mostrar `categoria.py` primero]**

VOZ:

"El modelado se realizó íntegramente con SQLModel, que combina Pydantic para validación y SQLAlchemy para el ORM, permitiéndonos definir entidades con tipado estático desde Python.

Tenemos tres entidades principales: Categoria, Producto e Ingrediente.

**[Mostrar el código de Categoria en el IDE]**

Comencemos por Categoria, que tiene una característica especial: es jerárquica. Usa un campo `parent_id` que es una foreign key a sí misma. Esto permite que una categoría tenga una categoría padre y varias subcategorías. Por ejemplo, podríamos tener una categoría 'Bebidas' y dentro de ella 'Bebidas Alcohólicas' y 'Bebidas Sin Alcohol'. El Relationship `parent` con `remote_side` permite navegar hacia arriba la jerarquía, mientras que `children` permite navegar hacia abajo. También tiene un campo `activo` de tipo booleano para implementar soft delete, es decir, marcar registros como eliminados sin borrarlos realmente de la base de datos.

**[Cambiar a `producto.py`]**

La relación entre Categoria y Producto es uno a muchos, es decir 1:N. Un producto pertenece siempre a una única categoría, pero una categoría puede contener muchos productos. Implementamos esto con `categoria_id` como foreign key en Producto. El Relationship con `back_populates` permite navegar en ambas direcciones: desde una categoría accedemos a todos sus productos, y desde un producto accedemos a su categoría directamente.

El campo `ingrediente_links` es una Lista de ProductoIngrediente con `cascade_delete=True`, lo que significa que si eliminamos un producto, automáticamente se eliminarán todos los links a sus ingredientes.

**[Cambiar a `producto_ingrediente.py`]**

La relación entre Producto e Ingrediente es muchos a muchos, es decir N:N. Un producto puede tener muchos ingredientes y un ingrediente puede estar en muchos productos distintos. Para esto creamos la tabla intermedia ProductoIngrediente. Pero aquí viene lo importante: no es solo un link vacío. Además de las claves foráneas, almacena el campo `cantidad`, que indica cuánto de ese ingrediente lleva el producto.

Usamos una **clave primaria compuesta** formada por `producto_id` e `ingrediente_id` juntos. Esto garantiza por diseño que no sea posible asignar el mismo ingrediente dos veces al mismo producto, sin necesidad de lógica extra en el código.

También el `ondelete="CASCADE"` en `producto_id` significa que si eliminamos un producto, todos sus ingredientes se eliminan en cascada automáticamente. Esta es precisamente la inteligencia que el diseño de datos proporciona.

Todos estos campos tienen validaciones: nombres con longitud mínima 2 caracteres, precios mayores a cero, cantidades positivas. Estas restricciones se declaran directamente en el modelo con Field, y Pydantic las valida automáticamente en cada entrada."

---

## 🎬 SECCIÓN 3 — ROUTERS, VALIDACIONES DECLARATIVAS Y EXCEPCIONES
### 🎤 Fabrizio Castillo | Routers, Validaciones Declarativas y Excepciones | ⏱ ~3 min

**[Abrir `backend/routers/` — mostrar `categorias.py` y luego `productos.py`]**

VOZ:

"Los routers son el puente entre HTTP y la lógica de negocio. En FastAPI, la validación empieza aquí con Annotated y los parámetros de Query.

**[Mostrar categorias.py — router GET /?]**

Por ejemplo, en el endpoint de listado de categorías, el parámetro `nombre` tiene `Query(max_length=50)`. Si el cliente manda una cadena más larga, FastAPI la rechaza antes de que llegue al servicio, respondiendo con 422 Unprocessable Entity y un detalle de Pydantic.

El parámetro `offset` tiene `Query(ge=0)`, lo que significa 'mayor o igual a cero'. El `limit` tiene `Query(ge=1, le=100)`, rango entre 1 y 100. Estas restricciones son declarativas: el router describe exactamente qué acepta.

El `response_model` es fundamental. Si el endpoint retorna una lista de Categoria pero marcamos `response_model=list[Categoria]`, FastAPI filtra automáticamente cualquier campo que no esté en el schema, protegiéndonos sin necesidad de lógica extra.

**[Mostrar productos.py — router POST /?]**

En el endpoint de creación, el router recibe un Producto, llama al servicio y retorna con `status_code=201 Created`. Cuando se actualiza algo, es `200 OK`. Cuando se elimina, es `204 No Content` sin cuerpo en la respuesta. Respetamos estrictamente los estándares HTTP. Si algo no existe, el servicio lanza `HTTPException(status_code=404)`. Si hay un conflicto de negocio, es `400` o `409`.

**[Abrir `backend/main.py` — mostrar el exception_handler]**

Aquí viene algo especial: tenemos excepciones personalizadas. En `main.py`, el handler de `DuplicateNameError` intercepta excepciones personalizadas de negocio y las convierte a respuestas HTTP 409 Conflict. El cliente recibe un JSON con el detalle, el código de error específico y el nombre que causó el conflicto.

Esto significa que la lógica de negocio puede lanzar excepciones específicas sin preocuparse por convertirlas a HTTP. El handler global lo hace automáticamente. Es una separación clara de responsabilidades: el negocio maneja su lógica, el router maneja HTTP, y el exception handler traduce entre ellos.

CORS también está configurado aquí, permitiendo que el frontend en localhost pueda llamar a estos endpoints."

---

## 🎬 SECCIÓN 4 — LÓGICA DE NEGOCIO: SERVICIOS Y REGLAS
### 🎤 Manuel Planero | Lógica de Negocio: Servicios y Reglas | ⏱ ~3 min

**[Abrir `backend/services/` — mostrar `categoria_service.py` y `producto_service.py`]**

VOZ:

"Toda la inteligencia de la aplicación está en los servicios. Un router solo valida esquemas y llama al servicio. Un servicio es quien piensa, decide y ejecuta la lógica de negocio.

**[Mostrar categoria_service.py — método get_all]**

Por ejemplo, en `CategoriaService.get_all()`, si el cliente manda un `nombre`, buscamos solo categorías que coincidan. Si no manda nada, retornamos todas, paginadas. Esa decisión está en el servicio, no en el router.

**[Mostrar el método get_by_id]**

Si solicitan una categoría por ID y no existe, el servicio lanza `HTTPException(404)`. Es el servicio quien sabe qué es una categoría válida.

**[Mostrar el método update]**

En la actualización, el servicio primero verifica que la categoría existe usando `get_by_id()`, luego actualiza cada campo, y finalmente realiza el commit a través del Unit of Work. Si algo falla en el medio, todo se hace rollback.

**[Mostrar método esta_en_uso]**

Hay un método especial llamado `esta_en_uso()`. Verifica si una categoría tiene productos asociados. Si tiene, retorna un JSON indicando cuántos. Esto permite que el frontend pregunte antes de intentar eliminar: "¿seguro que querés eliminar una categoría que tiene 5 productos?"

**[Cambiar a producto_service.py — mostrar agregar_ingrediente]**

En ProductoService, el método `agregar_ingrediente()` maneja la prevención de duplicados. Antes de insertar, pregunta: ¿este ingrediente ya está en este producto? Si existe, lanza `HTTPException(400)` con un mensaje claro. Si no existe, crea el link ProductoIngrediente con la cantidad indicada.

**[Mostrar quitar_ingrediente]**

Al quitar un ingrediente, primero buscamos el link. Si no existe, lanzamos 404. Si existe, lo eliminamos.

**[Mostrar método get_all]**

En `get_all()` aplicamos búsquedas por nombre, por categoría, o ambas. El servicio decide qué método del repositorio llamar según los parámetros. Luego refrescamos la sesión y forzamos la carga de `ingrediente_links` para garantizar que el cliente recibe los datos completos. Es un detalle importante que el servicio coordina."

---

## 🎬 SECCIÓN 5 — UNIT OF WORK, REPOSITORIOS Y DEMO EN VIVO
### 🎤 Uriel Rojas | Unit of Work, Repositorios y Demo en Vivo | ⏱ ~3 min

#### Parte 1: Unit of Work y Repositorios (~1 min)

**[Abrir `backend/uow/unit_of_work.py`]**

VOZ:

"Para la persistencia usamos el patrón Unit of Work junto con Repositorios. En `unit_of_work.py`, el UoW agrupa múltiples operaciones de base de datos en una sesión atómica.

**[Mostrar el init y el with context manager]**

El UoW se inicializa con una sesión SQLModel. Expone cuatro repositorios: categorias, ingredientes, productos, y producto_ingredientes.

Implementamos el protocolo context manager con `__enter__` y `__exit__`. Cuando usamos `with uow:`, el UoW entra automáticamente en el contexto. Si todo va bien, en `__exit__` hacemos commit. Si hay una excepción, hacemos rollback automáticamente. Esto garantiza que todas las operaciones dentro del with se ejecuten atómicamente, o ninguna.

**[Mostrar los repositorios en uow/ — producto_repository.py]**

**[Abrir producto_repository.py — mostrar algunos métodos]**

Cada repositorio hereda de `Repository` base, que proporciona operaciones CRUD genéricas: `get_all()`, `get_by_id()`, `create()`, `update()`, `delete()`. Los repositorios específicos extienden esto con búsquedas personalizadas como `find_by_nombre()`, `find_by_categoria()`, etc.

Esto es importante: el repositorio sabe cómo hablar con la base de datos, pero el servicio sabe qué lógica aplicar. Están separados.

La base de datos que usamos es SQLite para desarrollo, pero la configuración en `database.py` está lista para PostgreSQL con solo cambiar la URL de conexión."

#### Parte 2: Demo en Vivo (~2 min)

**[Mostrar terminal con uvicorn corriendo y navegador con la app]**

VOZ:

"Ahora hacemos la demo completa. El backend está corriendo con uvicorn y el frontend con Vite.

**[Navegar a la sección de Categorías en la app]**

Primero creamos una nueva categoría. Hago clic en 'Nueva Categoría', se abre un modal. Completo el nombre, la descripción, y elijo una categoría padre para crear una jerarquía.

**[Mostrar el formulario modal abierto]**

Guardo. En la consola de red del navegador vemos que se ejecutó un POST a `/categorias/` y el backend respondió con **201 Created**.

**[Mostrar la Network tab con el 201]**

La tabla de categorías se actualiza automáticamente gracias a la invalidación de caché de TanStack Query.

Ahora edito ese mismo registro. Hago clic en el botón de edición, el modal se precarga con los datos actuales. Cambio el nombre y guardo. Se ejecutó un PUT con **200 OK**. La UI se actualiza al instante.

**[Mostrar Network tab con el 200 OK]**

Acá demuestro las validaciones. Si intento guardar un nombre vacío o con menos de 2 caracteres, el frontend valida primero. Pero si intento hacer un ataque HTTP directo mandando datos inválidos, FastAPI rechaza la petición con **422 Unprocessable Entity**. El cliente recibe un mensaje de error detallado generado por Pydantic.

**[Mostrar un error 422 en la consola de network]**

Finalmente, intento eliminar una categoría que tiene productos. El servicio detecta que `esta_en_uso()` retorna `True`, y el frontend muestra una advertencia: 'No se puede eliminar una categoría que contiene 5 productos'. Esto previene inconsistencias.

Luego, elimino una categoría sin productos. El backend responde con **204 No Content** y la tabla se limpia sola.

**[Mostrar Network tab con 204]**

Esto cierra el flujo completo de CRUD: Crear, Leer, Actualizar, Eliminar. Todo conectado entre React en el frontend, FastAPI en el backend, con persistencia real en base de datos, manejo de errores, validaciones, jerarquías de categorías, y relaciones N:N con cantidades. La arquitectura en capas permite que cada pieza sea independiente, testeable y mantenible.

Gracias a todos."

---

## 📋 Indicaciones de Pantalla para el Editor de Video

| Sección | Segundo aprox. | Indicación de Pantalla |
|---|---|---|
| Intro | 0:00 - 0:15 | Pantalla de título o estructura IDE |
| Intro | 0:15 - 1:00 | Mostrar `backend/` — estructura de carpetas |
| Agustín - Categorías | 1:00 - 1:30 | Código: `models/categoria.py` — resaltar parent_id, Relationships |
| Agustín - Producto | 1:30 - 1:50 | Código: `models/producto.py` — resaltar categoria_id, ingrediente_links |
| Agustín - Relación N:N | 1:50 - 2:30 | Código: `models/producto_ingrediente.py` — resaltar PK compuesta, cascade |
| Fabrizio - Validaciones | 2:30 - 3:00 | Código: `routers/categorias.py` GET / — resaltar Query validators |
| Fabrizio - Routers POST/PUT/DELETE | 3:00 - 3:30 | Código: `routers/productos.py` — mostrar status_code |
| Fabrizio - Excepciones | 3:30 - 4:00 | Código: `main.py` exception_handler + `exceptions.py` |
| Manuel - Servicios | 4:00 - 5:00 | Código: `services/categoria_service.py` get_all, get_by_id, update, esta_en_uso |
| Manuel - ProductoService | 5:00 - 5:45 | Código: `services/producto_service.py` agregar_ingrediente, quitar_ingrediente |
| Uriel - UoW | 5:45 - 6:30 | Código: `uow/unit_of_work.py` __enter__, __exit__, context manager |
| Uriel - Repositorios | 6:30 - 7:00 | Código: `uow/producto_repository.py` — algunos métodos |
| Demo - Crear categoría | 7:00 - 7:45 | App UI + Network tab (POST 201) |
| Demo - Editar categoría | 7:45 - 8:30 | App UI + Network tab (PUT 200) |
| Demo - Validaciones | 8:30 - 9:30 | App UI + Network tab (422 Unprocessable Entity) |
| Demo - Verificar en uso | 9:30 - 10:15 | App UI — intentar eliminar categoría con productos |
| Demo - Eliminar categoría | 10:15 - 11:00 | App UI + Network tab (DELETE 204) |
| Cierre | 11:00 - 15:00 | Pantalla final o resumen visual |

---

## ⏱ Control de Tiempos

| Integrante | Sección | Tiempo Estimado |
|---|---|---|
| Joaquín | Intro + Ecosistema del Proyecto | ~3 min |
| Agustín | Modelado: Relaciones, Jerarquías y Validación | ~3 min |
| Fabrizio | Routers, Validaciones Declarativas y Excepciones | ~3 min |
| Manuel | Lógica de Negocio: Servicios y Reglas | ~3 min |
| Uriel | Unit of Work, Repositorios y Demo en Vivo | ~3 min |
| **TOTAL** | | **~15 min** |

---

## ✅ Checklist Antes de Grabar

- [ ] Backend corriendo: `python -m uvicorn main:app --reload`
- [ ] Frontend corriendo: `npm run dev` o `yarn dev`
- [ ] Base de datos con datos de prueba cargados
- [ ] Swagger abierto en pestaña aparte: `localhost:8000/docs`
- [ ] Consola de red del navegador visible (F12 → Network tab)
- [ ] Terminal del backend visible para mostrar logs
- [ ] Micrófono probado, resolución en 1080p mínimo
- [ ] Cada integrante tiene su parte del guión visible
- [ ] Ejemplos de UI (crear, editar, eliminar, validaciones) listos para demostrar
- [ ] Acceso rápido a archivos de código en el IDE (o tabs abiertos)
