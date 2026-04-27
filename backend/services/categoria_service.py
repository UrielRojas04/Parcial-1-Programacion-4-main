from fastapi import HTTPException
from sqlmodel import Session, select, func
from models.categoria import Categoria
from models.producto import Producto
from uow import UnitOfWork


class CategoriaService:
    
    def __init__(self, session: Session):
        self.uow = UnitOfWork(session)
    
    def get_all(self, nombre: str | None = None, offset: int = 0, limit: int = 10) -> list[Categoria]:
        if nombre:
            return self.uow.categorias.find_by_nombre(nombre)[offset:offset + limit]
        return self.uow.categorias.get_all(offset, limit)
    
    def get_by_id(self, categoria_id: int) -> Categoria:
        categoria = self.uow.categorias.get_by_id(categoria_id)
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoria no encontrada")
        return categoria
    
    def create(self, categoria: Categoria) -> Categoria:
        with self.uow:
            new_cat = self.uow.categorias.create(categoria)
            self.uow.session.refresh(new_cat)
            return new_cat
    
    def update(self, categoria_id: int, datos: Categoria) -> Categoria:
        with self.uow:
            categoria = self.get_by_id(categoria_id)
            categoria.nombre = datos.nombre
            categoria.descripcion = datos.descripcion
            categoria.parent_id = datos.parent_id
            categoria = self.uow.categorias.update(categoria)
            self.uow.session.refresh(categoria)
            return categoria
    
    def delete(self, categoria_id: int) -> None:
        with self.uow:
            self.get_by_id(categoria_id)
            self.uow.categorias.delete(categoria_id)

    def esta_en_uso(self, categoria_id: int) -> dict:
        self.get_by_id(categoria_id)
        
        statement = select(func.count()).select_from(Producto).where(
            Producto.categoria_id == categoria_id
        )
        cantidad = self.uow.session.exec(statement).one()
        
        return {
            "en_uso": cantidad > 0,
            "cantidad": cantidad
        }