from fastapi import APIRouter, Depends, Query
from typing import Annotated, Optional
from sqlmodel import Session
from database import get_session
from models.producto import Producto
from schemas.schemas import ProductoCreate, ProductoIngredienteCreate, ProductoRead
from services.producto_service import ProductoService

router = APIRouter(prefix="/productos", tags=["Productos"])

SessionDep = Annotated[Session, Depends(get_session)]


def get_producto_service(session: SessionDep) -> ProductoService:
    return ProductoService(session)


ProductoServiceDep = Annotated[ProductoService, Depends(get_producto_service)]


@router.get("/", response_model=list[ProductoRead])
def get_productos(
    service: ProductoServiceDep,
    nombre: Annotated[Optional[str], Query(max_length=100)] = None,
    categoria_id: Annotated[Optional[int], Query(ge=1)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return service.get_all(nombre, categoria_id, offset, limit)


@router.get("/{producto_id}", response_model=ProductoRead)
def get_producto(producto_id: int, service: ProductoServiceDep):
    return service.get_by_id(producto_id)


@router.post("/", response_model=ProductoRead, status_code=201)
def crear_producto(producto: Producto, service: ProductoServiceDep):
    return service.create(producto)


@router.put("/{producto_id}", response_model=ProductoRead)
def editar_producto(producto_id: int, datos: Producto, service: ProductoServiceDep):
    return service.update(producto_id, datos)


@router.delete("/{producto_id}", status_code=204)
def eliminar_producto(producto_id: int, service: ProductoServiceDep):
    service.delete(producto_id)


@router.get("/{producto_id}/ingredientes")
def get_ingredientes_producto(producto_id: int, service: ProductoServiceDep):
    return service.get_ingredientes(producto_id)


@router.post("/{producto_id}/ingredientes", status_code=201)
def agregar_ingrediente(
    producto_id: int,
    datos: ProductoIngredienteCreate,
    service: ProductoServiceDep
):
    return service.agregar_ingrediente(producto_id, datos)


@router.delete("/{producto_id}/ingredientes/{ingrediente_id}", status_code=204)
def quitar_ingrediente(
    producto_id: int,
    ingrediente_id: int,
    service: ProductoServiceDep
):
    service.quitar_ingrediente(producto_id, ingrediente_id)