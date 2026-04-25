# 🚀 GUÍA RÁPIDA PARA PREGUNTAS DEL PROFESOR (Backend)

## 1️⃣ RELACIONES (La pregunta más probable)

### Pregunta: "¿Cómo implementaste relación 1:N?"
**Respuesta corta:**
```python
class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    productos: List["Producto"] = Relationship(back_populates="categoria")

class Producto(SQLModel, table=True):
    categoria_id: Optional[int] = Field(foreign_key="categoria.id")
    categoria: Optional["Categoria"] = Relationship(back_populates="productos")
```
**En una frase:** Una categoría TIENE MUCHOS productos (1:N). Usamos `foreign_key` para conectar y `Relationship` + `back_populates` para la relación bidireccional.

---

### Pregunta: "¿Cómo implementaste relación N:N?"
**Respuesta corta:**
```python
# Tabla intermedia
class ProductoIngrediente(SQLModel, table=True):
    producto_id: Optional[int] = Field(foreign_key="producto.id", primary_key=True)
    ingrediente_id: Optional[int] = Field(foreign_key="ingrediente.id", primary_key=True)
    cantidad: float = Field(gt=0)
    producto: Optional["Producto"] = Relationship(back_populates="ingrediente_links")
    ingrediente: Optional["Ingrediente"] = Relationship(back_populates="producto_links")

# En Producto
ingrediente_links: List["ProductoIngrediente"] = Relationship(back_populates="producto")

# En Ingrediente
producto_links: List["ProductoIngrediente"] = Relationship(back_populates="ingrediente")
```
**En una frase:** Muchos productos tienen muchos ingredientes. Usamos tabla intermedia `ProductoIngrediente` que almacena las claves foráneas + cantidad.

---

## 2️⃣ VALIDACIONES

### Pregunta: "¿Dónde validas los datos?"
**Respuesta:**
```python
class Categoria(SQLModel):
    nombre: str = Field(min_length=2, max_length=50)  # ← Validación automática
    descripcion: Optional[str] = Field(max_length=200)

class Producto(SQLModel):
    precio: float = Field(gt=0)  # ← "greater than 0"
```
- **Schemas** = validan entrada (qué recibe el router)
- **Models** = validan entidad (qué va a la BD)
- **Annotated[Optional[str], Query(max_length=50)]** = validan query params

**Si envían datos inválidos → FastAPI retorna 422 Unprocessable Entity automáticamente.**

---

## 3️⃣ ENDPOINTS y CODES

### Pregunta: "¿Por qué algunos endpoints tienen status_code=201?"
**Respuesta:**
```python
@router.post("/", response_model=Categoria, status_code=201)  # 201 = Created
def crear_categoria(categoria: Categoria, service: CategoriaServiceDep):
    return service.create(categoria)

@router.delete("/{id}", status_code=204)  # 204 = No Content (sin body)
def eliminar_categoria(categoria_id: int, service: CategoriaServiceDep):
    service.delete(categoria_id)
```
- **201 Created** = recurso nuevo creado
- **200 OK** = request exitoso con respuesta
- **204 No Content** = delete/put exitoso sin respuesta
- **404 Not Found** = recurso no existe
- **400 Bad Request** = datos inválidos

---

## 4️⃣ ANNOTATED + QUERY

### Pregunta: "¿Qué es Annotated y por qué lo usas?"
**Respuesta:**
```python
@router.get("/")
def get_productos(
    nombre: Annotated[Optional[str], Query(max_length=100)] = None,
    categoria_id: Annotated[Optional[int], Query(ge=1)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    pass
```
**En una frase:** `Annotated[Type, Constraint]` = tipado fuerte + validación automática. FastAPI valida estos parámetros ANTES de que lleguen a la función.

**Validaciones que FastAPI hace:**
- `ge=0` = "greater than or equal 0" → rechaza negativos
- `le=100` = "less than or equal 100" → rechaza > 100
- `max_length=100` = rechaza strings largos
- Si no cumplen → retorna 422

---

## 5️⃣ SERVICIOS

### Pregunta: "¿Cuál es la diferencia entre un Router y un Service?"

| | Router | Service |
|---|---|---|
| **Qué hace** | Recibe/devuelve HTTP | Lógica de negocio |
| **Validación** | Entrada/salida HTTP | Validaciones lógicas (¿existe?) |
| **Base de datos** | NO accede | SÍ accede |
| **HTTPException** | NO lanza | SÍ lanza (404, 400) |

**Ejemplo:**
```python
# ROUTER: solo recibe y devuelve
@router.get("/{categoria_id}")
def get_categoria(categoria_id: int, service: CategoriaServiceDep):
    return service.get_by_id(categoria_id)

# SERVICE: valida y opera
class CategoriaService:
    def get_by_id(self, categoria_id: int):
        categoria = self.uow.categorias.get_by_id(categoria_id)
        if not categoria:
            raise HTTPException(status_code=404)  # ← validación
        return categoria
```

---

## 6️⃣ UNIT OF WORK

### Pregunta: "¿Qué es UnitOfWork?"
**Respuesta:**
```python
class UnitOfWork:
    def __init__(self, session):
        self.categorias = CategoriaRepository(session)
        self.ingredientes = IngredienteRepository(session)
        self.productos = ProductoRepository(session)
        self.producto_ingredientes = ProductoIngredienteRepository(session)
    
    def commit(self):
        self.session.commit()  # Confirma TODAS las operaciones
```

**En una frase:** UoW centraliza todos los repositorios + controla transacciones. `commit()` confirma TODOS los cambios a la vez.

---

## 7️⃣ TRANSACCIONES (Commit/Refresh/Flush)

### Pregunta: "¿Por qué llamás a refresh()?"
```python
def create(self, categoria: Categoria):
    categoria = self.uow.categorias.create(categoria)  # flush()
    self.uow.commit()  # confirma
    self.uow.session.refresh(categoria)  # recarga (obtiene id generado)
    return categoria
```
**Respuesta:** 
- `flush()` = prepara el INSERT (aún no en BD)
- `commit()` = confirma en BD (la BD genera el id)
- `refresh()` = sincroniza el objeto Python con la BD (obtiene el id)

Sin refresh(), el objeto no tendría el id generado.

---

## 8️⃣ FLUJO COMPLETO

### Pregunta: "Explicá qué pasa cuando alguien hace POST /categorias/"

```
1. Cliente envía:
   POST /categorias/
   {
       "nombre": "Postres",
       "descripcion": "..."
   }

2. FastAPI:
   - Valida: nombre 2-50 caracteres ✓
   - Crea objeto Categoria
   - Inyecta dependencias (Session, Service)

3. Router:
   crear_categoria(categoria, service)
   return service.create(categoria)

4. Service:
   def create(self, categoria):
       categoria = self.uow.categorias.create(categoria)
       # Flujo:
       # - session.add(categoria)
       # - session.flush()
       # → SQL: INSERT INTO categoria VALUES (...)
       
       self.uow.commit()
       # → SQL: COMMIT
       # → BD genera: id = 5
       
       self.uow.session.refresh(categoria)
       # → Recarga el objeto con id=5
       
       return categoria

5. Router devuelve:
   {
       "id": 5,
       "nombre": "Postres",
       "descripcion": "..."
   }

6. Cliente recibe:
   Status: 201 Created
   Body: {id, nombre, descripcion}
```

---

## 9️⃣ LAZY LOADING (Ingredientes en Producto)

### Pregunta: "¿Cómo accedes a los ingredientes de un producto?"

```python
# En ProductoService
def get_by_id(self, producto_id: int):
    producto = self.uow.session.get(Producto, producto_id)
    
    # ingrediente_links aún NO está cargado (lazy)
    self.uow.session.refresh(producto)
    _ = producto.ingrediente_links  # ← Carga aquí
    
    return producto

# Ahora producto.ingrediente_links = [
#     ProductoIngrediente(producto_id=1, ingrediente_id=5, cantidad=500),
#     ProductoIngrediente(producto_id=1, ingrediente_id=3, cantidad=12),
# ]
```

**Respuesta:** Las relaciones N:N se cargan bajo demanda (lazy). Necesitás acceder para que se carguen.

---

## 🔟 VALIDACIÓN DE DUPLICADOS (Agregando ingredientes)

### Pregunta: "¿Cómo prevenis duplicados en ProductoIngrediente?"

```python
def agregar_ingrediente(self, producto_id: int, datos: ProductoIngredienteCreate):
    # Busca si ya existe esta combinación
    existente = self.uow.producto_ingredientes.find_by_producto_e_ingrediente(
        producto_id, datos.ingrediente_id
    )
    
    if existente:
        raise HTTPException(
            status_code=400,
            detail="El ingrediente ya está en el producto"
        )
    
    # Si no existe, inserta
    link = ProductoIngrediente(...)
    self.uow.producto_ingredientes.create(link)
    self.uow.commit()
    return link
```

**Respuesta:** Buscas ANTES de insertar. Si existe → 400 Bad Request. Si no → inserta.

---

## 🎯 LAS 5 PREGUNTAS MÁS PROBABLES

1. **"¿Cómo implementaste la relación 1:N?"** → foreign_key + Relationship + back_populates
2. **"¿Cómo implementaste la relación N:N?"** → tabla intermedia ProductoIngrediente
3. **"¿Dónde validas?"** → Models/Schemas con Field(), Annotated en routers
4. **"¿Qué es Annotated?"** → tipado fuerte + validación automática
5. **"¿Qué es HTTPException?"** → forma standard FastAPI para retornar errores HTTP

---

## 📝 NOTA IMPORTANTE

Todos estos archivos tienen anotaciones detalladas:
- `models/categoria.py`
- `models/producto.py`
- `models/ingrediente.py`
- `models/producto_ingrediente.py`
- `schemas.py`
- `routers/categorias.py` (READ primero, es la más simple)
- `routers/productos.py` (LA MÁS COMPLEJA)
- `services/categoria_service.py` (lógica básica)
- `services/producto_service.py` (manejo de N:N)
- `uow/repository.py` (patrón genérico)
- `uow/unit_of_work.py` (orquestador)
- `database.py`
- `main.py`

**Orden de lectura recomendado si el profesor pregunta:**
1. Models → entiende relaciones
2. Schemas → entiende validación
3. Routers → entiende endpoints
4. Services → entiende lógica
5. UoW + Repository → entiende persistencia

¡Dale! Listos los archivos para que estudies. Ahora falta completar el frontend para el video.
