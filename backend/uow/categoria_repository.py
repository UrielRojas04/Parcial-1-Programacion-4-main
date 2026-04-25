from typing import Optional, List
from sqlmodel import Session, select
from models.categoria import Categoria
from .repository import BaseRepository


class CategoriaRepository(BaseRepository[Categoria]):
    """Repositorio específico para Categoria"""
    
    def __init__(self, session: Session):
        super().__init__(session, Categoria)
    
    def find_by_nombre(self, nombre: str) -> List[Categoria]:
        """Busca categorías por nombre (contiene)"""
        statement = select(Categoria).where(Categoria.nombre.contains(nombre))
        return self.session.exec(statement).all()
