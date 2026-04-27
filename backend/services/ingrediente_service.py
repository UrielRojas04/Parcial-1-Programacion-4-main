from fastapi import HTTPException
from sqlmodel import Session, select, func
from models.ingrediente import Ingrediente
from models.producto_ingrediente import ProductoIngrediente
from uow import UnitOfWork


class IngredienteService:
    
    def __init__(self, session: Session):
        self.uow = UnitOfWork(session)
    
    def get_all(self, nombre: str | None = None, offset: int = 0, limit: int = 10) -> list[Ingrediente]:
        if nombre:
            return self.uow.ingredientes.find_by_nombre(nombre)[offset:offset + limit]
        return self.uow.ingredientes.get_all(offset, limit)
    
    def get_by_id(self, ingrediente_id: int) -> Ingrediente:
        ingrediente = self.uow.ingredientes.get_by_id(ingrediente_id)
        if not ingrediente:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
        return ingrediente
    
    def create(self, ingrediente: Ingrediente) -> Ingrediente:
        ingrediente = self.uow.ingredientes.create(ingrediente)
        self.uow.commit()
        self.uow.session.refresh(ingrediente)
        return ingrediente
    
    def update(self, ingrediente_id: int, datos: Ingrediente) -> Ingrediente:
        ingrediente = self.get_by_id(ingrediente_id)
        ingrediente.nombre = datos.nombre
        ingrediente.unidad = datos.unidad
        ingrediente = self.uow.ingredientes.update(ingrediente)
        self.uow.commit()
        self.uow.session.refresh(ingrediente)
        return ingrediente
    
    def delete(self, ingrediente_id: int) -> None:
        self.get_by_id(ingrediente_id)
        self.uow.ingredientes.delete(ingrediente_id)
        self.uow.commit()

    def esta_en_uso(self, ingrediente_id: int) -> dict:
        self.get_by_id(ingrediente_id)
        
        statement = select(func.count()).select_from(ProductoIngrediente).where(
            ProductoIngrediente.ingrediente_id == ingrediente_id
        )
        cantidad = self.uow.session.exec(statement).one()
        
        return {
            "en_uso": cantidad > 0,
            "cantidad": cantidad
        }