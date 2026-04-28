from typing import Optional, List
from sqlmodel import Session, select, func
from models.categoria import Categoria
from .repository import BaseRepository


class CategoriaRepository(BaseRepository[Categoria]):
    """Repositorio específico para Categoria"""

    def __init__(self, session: Session):
        super().__init__(session, Categoria)

    def find_by_nombre(self, nombre: str) -> List[Categoria]:
        """Busca categorías por nombre (contiene, case-insensitive)"""
        statement = (
            select(Categoria)
            .where(func.lower(Categoria.nombre).contains(nombre.lower()))
            .where(Categoria.activo == True)
        )
        return self.session.exec(statement).all()

    def create(self, obj: Categoria) -> Categoria:
        """Crea una nueva categoría validando unicidad de nombre"""
        self.validate_nombre_uniqueness(obj.nombre)
        return super().create(obj)

    def update(self, obj: Categoria) -> Categoria:
        """Actualiza categoría validando unicidad de nombre (excluyendo el ID actual)"""
        self.validate_nombre_uniqueness(obj.nombre, exclude_id=obj.id)
        return super().update(obj)
