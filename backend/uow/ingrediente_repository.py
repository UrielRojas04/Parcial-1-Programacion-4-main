from typing import Optional, List
from sqlmodel import Session, select, func
from models.ingrediente import Ingrediente
from .repository import BaseRepository


class IngredienteRepository(BaseRepository[Ingrediente]):
    """Repositorio específico para Ingrediente"""

    def __init__(self, session: Session):
        super().__init__(session, Ingrediente)

    def find_by_nombre(self, nombre: str) -> List[Ingrediente]:
        """Busca ingredientes por nombre (contiene, case-insensitive)"""
        statement = select(Ingrediente).where(
            func.lower(Ingrediente.nombre).contains(nombre.lower()),
            Ingrediente.activo == True,
        )
        return self.session.exec(statement).all()

    def create(self, obj: Ingrediente) -> Ingrediente:
        """Crea un nuevo ingrediente validando unicidad de nombre"""
        self.validate_nombre_uniqueness(obj.nombre)
        return super().create(obj)

    def update(self, obj: Ingrediente) -> Ingrediente:
        """Actualiza ingrediente validando unicidad de nombre (excluyendo el ID actual)"""
        self.validate_nombre_uniqueness(obj.nombre, exclude_id=obj.id)
        return super().update(obj)
