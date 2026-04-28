from typing import Optional, List
from sqlmodel import Session, select, func
from models.producto import Producto
from .repository import BaseRepository


class ProductoRepository(BaseRepository[Producto]):
    """Repositorio específico para Producto"""

    def __init__(self, session: Session):
        super().__init__(session, Producto)

    def find_by_nombre(self, nombre: str) -> List[Producto]:
        """Busca productos por nombre (contiene)"""
        statement = select(Producto).where(
            Producto.nombre.contains(nombre), Producto.activo == True
        )
        return self.session.exec(statement).all()

    def find_by_categoria(
        self, categoria_id: int, offset: int = 0, limit: int = 10
    ) -> List[Producto]:
        """Busca productos por categoría"""
        statement = (
            select(Producto)
            .where(Producto.categoria_id == categoria_id, Producto.activo == True)
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def find_by_nombre_y_categoria(
        self, nombre: str, categoria_id: int, offset: int = 0, limit: int = 10
    ) -> List[Producto]:
        """Busca productos por nombre y categoría"""
        statement = (
            select(Producto)
            .where(
                Producto.nombre.contains(nombre), Producto.categoria_id == categoria_id
            )
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def buscar_con_filtros(
        self,
        nombre: str | None = None,
        categoria_id: int | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> List[Producto]:
        """Busca productos por filtros opcionales"""
        statement = select(Producto)
        if nombre:
            statement = statement.where(
                func.lower(Producto.nombre).contains(nombre.lower())
            )
        if categoria_id:
            statement = statement.where(
                Producto.categoria_id == categoria_id, Producto.activo == True
            )
        statement = statement.offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def contar_por_categoria(self, categoria_id: int) -> int:
        """Cuenta productos por categoría"""
        statement = (
            select(func.count())
            .select_from(Producto)
            .where(Producto.categoria_id == categoria_id)
        )
        return self.session.exec(statement).one()

    def create(self, obj: Producto) -> Producto:
        """Crea un nuevo producto validando unicidad de nombre"""
        self.validate_nombre_uniqueness(obj.nombre)
        return super().create(obj)

    def update(self, obj: Producto) -> Producto:
        """Actualiza producto validando unicidad de nombre (excluyendo el ID actual)"""
        self.validate_nombre_uniqueness(obj.nombre, exclude_id=obj.id)
        return super().update(obj)
