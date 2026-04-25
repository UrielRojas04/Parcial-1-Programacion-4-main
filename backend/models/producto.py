"""
MODELO: Producto
================
Representa un producto vendible con relaciones complejas.

CONCEPTOS CLAVE:
1. Relación 1:N con Categoria (muchos productos → una categoría)
2. Relación N:N con Ingrediente (muchos productos ↔ muchos ingredientes)
3. Foreign Key: conecta con otra tabla
4. TYPE_CHECKING: evita importaciones circulares

ESTRUCTURA:
- id: Identificador único
- nombre, precio, descripcion: Datos del producto
- categoria_id: Foreign Key hacia Categoria (1:N)
- categoria: Relación para acceder a la categoría
- ingrediente_links: Relación N:N hacia Ingredientes (vía ProductoIngrediente)

FLUJO EN LA APLICACIÓN:
1. Frontend envía POST /productos/ con {nombre, precio, categoria_id}
2. Backend crea Producto(...)
3. Se guarda en BD con referencia a categoria_id
4. Al leerlo, puede acceder a: producto.categoria.nombre
5. Para ingredientes: producto.ingrediente_links → lista de ProductoIngrediente
"""

from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .categoria import Categoria
    from .producto_ingrediente import ProductoIngrediente


class Producto(SQLModel, table=True):
    """Modelo para Producto"""
    
    # CAMPO: id (Clave Primaria)
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # CAMPO: nombre
    # Ej: "Torta de Chocolate", "Pizza Margherita"
    nombre: str = Field(min_length=2, max_length=100)
    
    # CAMPO: precio
    # precio: float = número decimal (3.50, 12.99, etc.)
    # Field(gt=0) = "greater than 0" → rechaza precios negativos o cero
    # Validación automática en FastAPI
    precio: float = Field(gt=0)
    
    # CAMPO: descripcion (Opcional)
    # Optional[str] = puede ser NULL
    # max_length=300 = descripción corta (sin exagerar)
    descripcion: Optional[str] = Field(default=None, max_length=300)

    # ========== RELACIÓN 1:N (Uno a Muchos) ==========
    # Un producto PERTENECE A una categoría
    # Muchos productos pueden estar en la MISMA categoría
    #
    # TABLA EN BD:
    # producto_id | nombre           | categoria_id
    # 1           | Torta Chocolate  | 2  (Categoría "Postres")
    # 2           | Pizza Margherita | 1  (Categoría "Platos")
    # 3           | Brownie          | 2  (Categoría "Postres")
    #
    # categoria_id: Optional[int]
    #   - Optional = puede ser NULL (producto sin categoría)
    #   - int = referencia al id de Categoria
    # Field(default=None, foreign_key="categoria.id")
    #   - foreign_key="categoria.id" → dice "esto referencia la tabla categoria, columna id"
    #   - Si intentas referenciar un categoria_id que NO existe → error de integridad
    categoria_id: Optional[int] = Field(default=None, foreign_key="categoria.id")
    
    # categoria: Relación para acceder desde Python
    # Optional["Categoria"] = puede ser None si categoria_id es NULL
    # Relationship(back_populates="productos")
    #   - back_populates="productos" → en Categoria, hay List["Producto"]
    #   - Crea una relación bidireccional AUTOMÁTICAMENTE
    #
    # ACCESO:
    # producto = db.get(Producto, 1)
    # categoria_nombre = producto.categoria.nombre  ← Lazy loaded (query automática)
    categoria: Optional["Categoria"] = Relationship(back_populates="productos")

    # ========== RELACIÓN N:N (Muchos a Muchos) ==========
    # Un producto TIENE MUCHOS ingredientes
    # Un ingrediente está EN MUCHOS productos
    #
    # TABLA INTERMEDIA (ProductoIngrediente):
    # producto_id | ingrediente_id | cantidad
    # 1           | 5              | 500      (Torta tiene 500g de Harina)
    # 1           | 3              | 12       (Torta tiene 12 Huevos)
    # 2           | 4              | 200      (Pizza tiene 200g de Queso)
    #
    # List["ProductoIngrediente"] = lista de VÍNCULOS (no ingredientes directos)
    # Para acceder al ingrediente: producto.ingrediente_links[0].ingrediente
    #
    # ACCESO:
    # producto = db.get(Producto, 1)
    # for link in producto.ingrediente_links:
    #     print(f"{link.ingrediente.nombre}: {link.cantidad} {link.ingrediente.unidad}")
    # OUTPUT:
    # Harina: 500 gramos
    # Huevo: 12 unidades
    ingrediente_links: List["ProductoIngrediente"] = Relationship(back_populates="producto", cascade_delete=True)
