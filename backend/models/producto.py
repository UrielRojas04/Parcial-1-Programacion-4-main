from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .categoria import Categoria
    from .producto_ingrediente import ProductoIngrediente


class Producto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=2, max_length=100)
    precio: float = Field(gt=0)
    descripcion: Optional[str] = Field(default=None, max_length=300)
    categoria_id: Optional[int] = Field(default=None, foreign_key="categoria.id")
    categoria: Optional["Categoria"] = Relationship(back_populates="productos")
    activo: bool = Field(default=True)
    ingrediente_links: List["ProductoIngrediente"] = Relationship(back_populates="producto", cascade_delete=True)