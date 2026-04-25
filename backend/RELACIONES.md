# Diagrama de Relaciones - Base de Datos

## Estructura Corregida ✅

```
┌─────────────────────────────────────────────────────────────────┐
│                        CATEGORIA                                │
├─────────────────────────────────────────────────────────────────┤
│  PK │ id              (int)                                      │
│     │ nombre          (str, 2-50)                               │
│     │ descripcion     (str, max 200, nullable)                  │
│     │                                                             │
│ REL │ productos[]     (1:N ← Producto.categoria_id)             │
└─────────────────────────────────────────────────────────────────┘
                            ▲
                            │ 1:N
                            │
┌─────────────────────────────────────────────────────────────────┐
│                        PRODUCTO                                 │
├─────────────────────────────────────────────────────────────────┤
│  PK │ id              (int)                                      │
│     │ nombre          (str, 2-100)                              │
│     │ precio          (float, > 0)                              │
│     │ descripcion     (str, max 300, nullable)                  │
│  FK │ categoria_id    (int → categoria.id, nullable)            │
│     │                                                             │
│ REL │ categoria       (1:N → Categoria.id)                      │
│ REL │ ingrediente_links[] (N:N ← ProductoIngrediente)           │
└─────────────────────────────────────────────────────────────────┘
            │
            │ N:N (a través de ProductoIngrediente)
            │
            ▼
┌──────────────────────────────────────────────────────────────────┐
│                  PRODUCTO_INGREDIENTE                            │
├──────────────────────────────────────────────────────────────────┤
│  PK, FK │ producto_id      (int → producto.id)                  │
│  PK, FK │ ingrediente_id   (int → ingrediente.id)               │
│         │ cantidad         (float, > 0)                         │
│         │                                                        │
│  REL    │ producto         (N:1 → Producto.id)                  │
│  REL    │ ingrediente      (N:1 → Ingrediente.id)               │
└──────────────────────────────────────────────────────────────────┘
            │
            │ N:N
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      INGREDIENTE                                │
├─────────────────────────────────────────────────────────────────┤
│  PK │ id              (int)                                      │
│     │ nombre          (str, 2-50)                               │
│     │ unidad          (str, max 20)                             │
│     │                                                             │
│ REL │ producto_links[] (N:N ← ProductoIngrediente)              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Relaciones Detalladas

### 1️⃣ Relación 1:N: Categoria ← Producto

**Tabla Categoria:**
```python
productos: List["Producto"] = Relationship(back_populates="categoria")
```

**Tabla Producto:**
```python
categoria_id: Optional[int] = Field(foreign_key="categoria.id")
categoria: Optional["Categoria"] = Relationship(back_populates="productos")
```

**Significado:** Una categoría puede tener muchos productos, pero cada producto pertenece a una sola categoría.

---

### 2️⃣ Relación N:N: Producto ↔ Ingrediente (con tabla intermedia)

**Tabla ProductoIngrediente (tabla pivot):**
```python
producto_id: Optional[int] = Field(foreign_key="producto.id", primary_key=True)
ingrediente_id: Optional[int] = Field(foreign_key="ingrediente.id", primary_key=True)
cantidad: float = Field(gt=0)

producto: Optional["Producto"] = Relationship(back_populates="ingrediente_links")
ingrediente: Optional["Ingrediente"] = Relationship(back_populates="producto_links")
```

**Tabla Producto:**
```python
ingrediente_links: List["ProductoIngrediente"] = Relationship(back_populates="producto")
```

**Tabla Ingrediente:**
```python
producto_links: List["ProductoIngrediente"] = Relationship(back_populates="ingrediente")
```

**Significado:** Un producto puede tener muchos ingredientes y un ingrediente puede estar en muchos productos. La tabla intermedia almacena la cantidad de cada ingrediente por producto.

---

## Ejemplos de Uso

### Acceder a productos de una categoría
```python
categoria = session.get(Categoria, 1)
productos = categoria.productos  # List[Producto]
```

### Acceder a ingredientes de un producto
```python
producto = session.get(Producto, 1)
ingredientes = [link.ingrediente for link in producto.ingrediente_links]
```

### Acceder a cantidad de ingrediente en un producto
```python
producto = session.get(Producto, 1)
for link in producto.ingrediente_links:
    print(f"{link.ingrediente.nombre}: {link.cantidad} {link.ingrediente.unidad}")
```

### Acceder a productos que contienen un ingrediente
```python
ingrediente = session.get(Ingrediente, 1)
productos = [link.producto for link in ingrediente.producto_links]
```

---

## Clave Primaria Compuesta

La tabla `producto_ingrediente` usa una **clave primaria compuesta**:
- `(producto_id, ingrediente_id)` es la clave primaria
- Esto asegura que no haya duplicados: un ingrediente aparece una sola vez por producto

```sql
-- La BD crea automáticamente esta constraint:
PRIMARY KEY (producto_id, ingrediente_id)
```

---

## Estado: ✅ CORRECTO

Todas las relaciones están correctamente implementadas:
- ✅ Categoria → Producto (1:N)
- ✅ Producto ↔ Ingrediente (N:N con tabla intermedia)
- ✅ ProductoIngrediente tiene campo de cantidad
- ✅ Back_populates bidireccionales configurados
- ✅ Foreign keys correctas
- ✅ TYPE_CHECKING para evitar circular imports
