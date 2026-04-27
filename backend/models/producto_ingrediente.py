from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .producto import Producto
    from .ingrediente import Ingrediente


class ProductoIngrediente(SQLModel, table=True):
    __tablename__ = "producto_ingrediente"
    
    producto_id: Optional[int] = Field(
        default=None, 
        foreign_key="producto.id", 
        ondelete="CASCADE",
        primary_key=True
    )
    
    ingrediente_id: Optional[int] = Field(
        default=None, 
        foreign_key="ingrediente.id", 
        primary_key=True
    )
    
    cantidad: float = Field(gt=0)
    producto: Optional["Producto"] = Relationship(back_populates="ingrediente_links")
    ingrediente: Optional["Ingrediente"] = Relationship(back_populates="producto_links")