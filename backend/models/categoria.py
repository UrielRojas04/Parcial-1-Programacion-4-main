from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .producto import Producto


class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=2, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=200)
    productos: List["Producto"] = Relationship(back_populates="categoria")