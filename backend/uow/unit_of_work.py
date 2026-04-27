from sqlmodel import Session
from .categoria_repository import CategoriaRepository
from .ingrediente_repository import IngredienteRepository
from .producto_repository import ProductoRepository
from .producto_ingrediente_repository import ProductoIngredienteRepository


class UnitOfWork:
    
    def __init__(self, session: Session):
        self.session = session
        self.categorias = CategoriaRepository(session)
        self.ingredientes = IngredienteRepository(session)
        self.productos = ProductoRepository(session)
        self.producto_ingredientes = ProductoIngredienteRepository(session)
    
    def commit(self):
        self.session.commit()
    
    def rollback(self):
        self.session.rollback()
    
    def close(self):
        self.session.close()