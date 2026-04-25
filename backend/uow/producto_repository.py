from typing import Optional, List
from sqlmodel import Session, select
from models.producto import Producto
from .repository import BaseRepository


class ProductoRepository(BaseRepository[Producto]):
    """Repositorio específico para Producto"""
    
    def __init__(self, session: Session):
        super().__init__(session, Producto)
    
    def find_by_nombre(self, nombre: str) -> List[Producto]:
        """Busca productos por nombre (contiene)"""
        statement = select(Producto).where(Producto.nombre.contains(nombre))
        return self.session.exec(statement).all()
    
    def find_by_categoria(self, categoria_id: int, offset: int = 0, limit: int = 10) -> List[Producto]:
        """Busca productos por categoría"""
        statement = select(Producto).where(Producto.categoria_id == categoria_id).offset(offset).limit(limit)
        return self.session.exec(statement).all()
    
    def find_by_nombre_y_categoria(self, nombre: str, categoria_id: int, offset: int = 0, limit: int = 10) -> List[Producto]:
        """Busca productos por nombre y categoría"""
        statement = select(Producto).where(
            Producto.nombre.contains(nombre),
            Producto.categoria_id == categoria_id
        ).offset(offset).limit(limit)
        return self.session.exec(statement).all()
