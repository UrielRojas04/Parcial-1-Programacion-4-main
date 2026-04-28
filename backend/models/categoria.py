from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .producto import Producto


class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="categoria.id")
    nombre: str = Field(min_length=2, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=200)
    parent: Optional["Categoria"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Categoria.id"}
    )
    children: List["Categoria"] = Relationship(back_populates="parent")
    productos: List["Producto"] = Relationship(back_populates="categoria")