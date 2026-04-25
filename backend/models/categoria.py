"""
MODELO: Categoria
=================
Representa una categoría de productos en la base de datos.

CONCEPTOS CLAVE:
1. SQLModel combina SQLAlchemy ORM + Pydantic validación
2. table=True indica que esto crea una tabla en PostgreSQL
3. Relaciones bidireccionales con back_populates

ESTRUCTURA:
- id: Identificador único (autoincremental)
- nombre: Texto validado (2-50 caracteres)
- descripcion: Texto opcional (max 200 caracteres)
- productos: Relación 1:N (una categoría → muchos productos)
"""

from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

# TYPE_CHECKING evita importación circular en tiempo de ejecución
# Se usa para type hints cuando las importaciones causarían ciclos
if TYPE_CHECKING:
    from .producto import Producto


class Categoria(SQLModel, table=True):
    """
    Modelo para Categoría de Productos
    Almacena categorías como: "Bebidas", "Postres", "Platos Principales"
    """
    
    # CAMPO: id (Clave Primaria)
    # Optional[int] = permite NULL antes de insertar (BD genera el valor)
    # Field(default=None, primary_key=True) = es PK, generada automáticamente
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # CAMPO: nombre
    # str = tipo obligatorio (no puede ser NULL)
    # Field(min_length=2, max_length=50) = validación automática de Pydantic
    # Si alguien envía nombre="" → FastAPI rechaza la request con error 422
    nombre: str = Field(min_length=2, max_length=50)
    
    # CAMPO: descripcion
    # Optional[str] = puede ser NULL en la BD
    # default=None = si no se envía, se guarda como NULL
    descripcion: Optional[str] = Field(default=None, max_length=200)

    # RELACIÓN 1:N (Uno a Muchos)
    # Una categoría TIENE MUCHOS productos
    # Ejemplo: Categoría "Bebidas" tiene [Coca, Fanta, Sprite, ...]
    #
    # List["Producto"] = puede ser 0, 1 o 100+ productos
    # Relationship = tell SQLModel "sincroniza esto en memoria"
    # back_populates="categoria" = crea la relación inversa en Producto
    #   → así Producto.categoria devuelve su categoría
    #   → y Categoria.productos devuelve todos sus productos
    #
    # El lazy loading se ejecuta solo cuando accedés: categoria.productos
    productos: List["Producto"] = Relationship(back_populates="categoria")
