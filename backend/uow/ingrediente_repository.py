from typing import Optional, List
from sqlmodel import Session, select
from models.ingrediente import Ingrediente
from .repository import BaseRepository


class IngredienteRepository(BaseRepository[Ingrediente]):
    """Repositorio específico para Ingrediente"""
    
    def __init__(self, session: Session):
        super().__init__(session, Ingrediente)
    
    def find_by_nombre(self, nombre: str) -> List[Ingrediente]:
        """Busca ingredientes por nombre (contiene)"""
        statement = select(Ingrediente).where(Ingrediente.nombre.contains(nombre))
        return self.session.exec(statement).all()
