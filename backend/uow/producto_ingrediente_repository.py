from typing import Optional
from sqlmodel import Session, select
from models.producto_ingrediente import ProductoIngrediente
from .repository import BaseRepository


class ProductoIngredienteRepository(BaseRepository[ProductoIngrediente]):
    
    def __init__(self, session: Session):
        super().__init__(session, ProductoIngrediente)
    
    def find_by_producto_e_ingrediente(
        self, producto_id: int, ingrediente_id: int
    ) -> Optional[ProductoIngrediente]:
        statement = select(ProductoIngrediente).where(
            ProductoIngrediente.producto_id == producto_id,
            ProductoIngrediente.ingrediente_id == ingrediente_id
        )
        return self.session.exec(statement).first()
    
    def find_by_producto(self, producto_id: int) -> list[ProductoIngrediente]:
        statement = select(ProductoIngrediente).where(
            ProductoIngrediente.producto_id == producto_id
        )
        return self.session.exec(statement).all()