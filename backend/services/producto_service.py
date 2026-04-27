from fastapi import HTTPException
from sqlmodel import Session, select
from models.producto import Producto
from models.producto_ingrediente import ProductoIngrediente
from schemas.schemas import ProductoIngredienteCreate
from uow import UnitOfWork


class ProductoService:

    def __init__(self, session: Session):
        self.uow = UnitOfWork(session)

    def get_all(self, nombre=None, categoria_id=None, offset=0, limit=10):
        from sqlalchemy import func
        statement = select(Producto)
        if nombre:
            statement = statement.where(func.lower(Producto.nombre).contains(nombre.lower()))
        if categoria_id:
            statement = statement.where(Producto.categoria_id == categoria_id)
        statement = statement.offset(offset).limit(limit)
        productos = self.uow.session.exec(statement).all()
        
        for producto in productos:
            self.uow.session.refresh(producto)
            _ = producto.ingrediente_links
        
        return productos

    def get_by_id(self, producto_id: int) -> Producto:
        producto = self.uow.session.get(Producto, producto_id)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        self.uow.session.refresh(producto)
        _ = producto.ingrediente_links
        
        return producto

    def create(self, producto: Producto) -> Producto:
        producto = self.uow.productos.create(producto)
        self.uow.commit()
        self.uow.session.refresh(producto)
        return producto

    def update(self, producto_id: int, datos: Producto) -> Producto:
        producto = self.get_by_id(producto_id)
        producto.nombre = datos.nombre
        producto.precio = datos.precio
        producto.descripcion = datos.descripcion
        producto.categoria_id = datos.categoria_id
        producto = self.uow.productos.update(producto)
        self.uow.commit()
        self.uow.session.refresh(producto)
        return producto

    def delete(self, producto_id: int) -> None:
        self.get_by_id(producto_id)
        self.uow.productos.delete(producto_id)
        self.uow.commit()

    def agregar_ingrediente(
        self, producto_id: int, datos: ProductoIngredienteCreate
    ) -> ProductoIngrediente:
        self.get_by_id(producto_id)

        existente = self.uow.producto_ingredientes.find_by_producto_e_ingrediente(
            producto_id, datos.ingrediente_id
        )
        if existente:
            raise HTTPException(
                status_code=400, 
                detail="El ingrediente ya está en el producto"
            )

        link = ProductoIngrediente(
            producto_id=producto_id,
            ingrediente_id=datos.ingrediente_id,
            cantidad=datos.cantidad
        )
        self.uow.producto_ingredientes.create(link)
        self.uow.commit()
        self.uow.session.refresh(link)
        return link
    
    def get_ingredientes(self, producto_id: int):
        self.get_by_id(producto_id)  
        statement = select(ProductoIngrediente).where(
            ProductoIngrediente.producto_id == producto_id
        )
        return self.uow.session.exec(statement).all()

    def quitar_ingrediente(self, producto_id: int, ingrediente_id: int) -> None:
        link = self.uow.producto_ingredientes.find_by_producto_e_ingrediente(
            producto_id, ingrediente_id
        )
        if not link:
            raise HTTPException(
                status_code=404, 
                detail="Relación no encontrada"
            )
        self.uow.session.delete(link)
        self.uow.commit()