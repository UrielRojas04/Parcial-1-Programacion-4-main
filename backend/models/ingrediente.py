from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .producto_ingrediente import ProductoIngrediente


class Ingrediente(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=2, max_length=50)
    unidad: str = Field(max_length=20)
    activo: bool = Field(default=True)
    producto_links: List["ProductoIngrediente"] = Relationship(back_populates="ingrediente")