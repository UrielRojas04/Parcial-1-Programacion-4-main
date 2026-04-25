"""
MODELO: Ingrediente
===================
Representa un ingrediente individual en el sistema.

CONCEPTOS CLAVE:
1. Es una entidad simple con relación N:N hacia Productos
2. La N:N se implementa a través de ProductoIngrediente
3. unidad: mide la cantidad ("gramos", "ml", "unidades", etc.)

ESTRUCTURA:
- id: Identificador único
- nombre: Nombre del ingrediente
- unidad: Unidad de medida
- producto_links: Relación N:N hacia productos (vía ProductoIngrediente)
"""

from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .producto_ingrediente import ProductoIngrediente


class Ingrediente(SQLModel, table=True):
    """
    Modelo para Ingrediente
    Ejemplos: "Harina", "Huevo", "Leche", "Azúcar", "Chocolate"
    """
    
    # CAMPO: id (Clave Primaria)
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # CAMPO: nombre
    # Ej: "Harina"
    nombre: str = Field(min_length=2, max_length=50)
    
    # CAMPO: unidad
    # Ej: "gramos", "ml", "taza", "cucharada"
    # max_length=20 porque no necesitamos descripciones largas
    unidad: str = Field(max_length=20)
    
    # RELACIÓN N:N (Muchos a Muchos)
    # Un ingrediente está en MUCHOS productos
    # Muchos productos usan este ingrediente
    #
    # ProductoIngrediente es la tabla intermedia que:
    # - Conecta Ingrediente con Producto
    # - Almacena la cantidad específica en cada producto
    #
    # Ejemplo:
    #   Ingrediente "Huevo" → está en [Torta, Pizza, Pasta, ...]
    #   Producto "Torta" → usa [Harina, Huevo, Leche, Azúcar, ...]
    #
    # producto_links: son los VÍNCULOS a productos (no los productos directo)
    # Para acceder al producto: ingrediente.producto_links[0].producto
    producto_links: List["ProductoIngrediente"] = Relationship(back_populates="ingrediente")
