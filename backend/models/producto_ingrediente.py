"""
MODELO: ProductoIngrediente (Tabla Intermedia N:N)
===================================================
Representa la relación muchos-a-muchos entre Producto e Ingrediente.

PROPÓSITO:
- Conectar un Producto con sus Ingredientes
- Almacenar la CANTIDAD específica de cada ingrediente en cada producto
- Sin esto, no podríamos saber si una Torta lleva 500g o 2kg de Harina

TABLA EN BD:
┌─────────────┬────────────────┬──────────┐
│ producto_id │ ingrediente_id │ cantidad │
├─────────────┼────────────────┼──────────┤
│ 1           │ 5              │ 500      │  Torta (id=1) tiene 500g de Harina (id=5)
│ 1           │ 3              │ 12       │  Torta (id=1) tiene 12 Huevos (id=3)
│ 2           │ 4              │ 200      │  Pizza (id=2) tiene 200g de Queso (id=4)
└─────────────┴────────────────┴──────────┘

CLAVE PRIMARIA COMPUESTA:
- No hay id autoincremental
- La PK es la combinación (producto_id, ingrediente_id)
- Esto previene duplicados: no puede haber 2 filas con mismo producto e ingrediente

RELACIONES BIDIRECCIONALES:
- back_populates="ingrediente_links" en Producto
- back_populates="producto_links" en Ingrediente
"""

from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .producto import Producto
    from .ingrediente import Ingrediente


class ProductoIngrediente(SQLModel, table=True):
    """
    Modelo de relación N:N entre Producto e Ingrediente
    Representa los ingredientes de cada producto con sus cantidades
    """
    
    # Nombre explícito de la tabla en la BD
    # Si no lo especificas, SQLModel genera uno automáticamente
    __tablename__ = "producto_ingrediente"
    
    # ========== CLAVE FORÁNEA 1: producto_id ==========
    # Apunta a: tabla "producto", columna "id"
    # Optional[int] = puede ser NULL (aunque lógicamente no debería)
    # default=None = antes de insertar, es NULL
    # foreign_key="producto.id" = referencia a Producto.id
    # primary_key=True = PARTE DE LA CLAVE PRIMARIA COMPUESTA
    #
    # FLUJO:
    # 1. Creas ProductoIngrediente(producto_id=1, ingrediente_id=5, cantidad=500)
    # 2. BD valida: ¿existe Producto con id=1? SÍ → inserta
    # 3. Si envías producto_id=999 (no existe) → ERROR de integridad referencial
    producto_id: Optional[int] = Field(
        default=None, 
        foreign_key="producto.id", 
        primary_key=True
    )
    
    # ========== CLAVE FORÁNEA 2: ingrediente_id ==========
    # Apunta a: tabla "ingrediente", columna "id"
    # primary_key=True = PARTE DE LA CLAVE PRIMARIA COMPUESTA
    # La combinación (producto_id, ingrediente_id) debe ser ÚNICA
    # No puede haber 2 filas iguales
    ingrediente_id: Optional[int] = Field(
        default=None, 
        foreign_key="ingrediente.id", 
        primary_key=True
    )
    
    # ========== CAMPO DE DATOS: cantidad ==========
    # cantidad: float = número decimal (500.5, 12.0, etc.)
    # Field(gt=0) = "greater than 0" → rechaza 0 y negativos
    # Ej: 500 (gramos), 12 (unidades), 0.5 (tazas)
    cantidad: float = Field(gt=0)
    
    # ========== RELACIÓN: producto ==========
    # Acceso al producto desde el vínculo
    # Optional["Producto"] = puede ser None si producto_id es NULL
    # Relationship(back_populates="ingrediente_links")
    #   - "ingrediente_links" es el atributo en Producto que apunta aquí
    #   - Crea la relación bidireccional automáticamente
    #
    # ACCESO:
    # link = db.get(ProductoIngrediente, (1, 5))  # producto_id=1, ingrediente_id=5
    # print(link.producto.nombre)  # "Torta de Chocolate"
    producto: Optional["Producto"] = Relationship(back_populates="ingrediente_links")
    
    # ========== RELACIÓN: ingrediente ==========
    # Acceso al ingrediente desde el vínculo
    # Optional["Ingrediente"] = puede ser None si ingrediente_id es NULL
    # Relationship(back_populates="producto_links")
    #   - "producto_links" es el atributo en Ingrediente que apunta aquí
    #
    # ACCESO:
    # link = db.get(ProductoIngrediente, (1, 5))
    # print(link.ingrediente.nombre)  # "Harina"
    # print(link.cantidad)             # 500
    # print(link.ingrediente.unidad)   # "gramos"
    ingrediente: Optional["Ingrediente"] = Relationship(back_populates="producto_links")
