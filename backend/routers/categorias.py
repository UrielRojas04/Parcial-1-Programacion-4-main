from fastapi import APIRouter, Depends, Query
from typing import Annotated, Optional
from sqlmodel import Session
from database import get_session
from models.categoria import Categoria
from services.categoria_service import CategoriaService

router = APIRouter(prefix="/categorias", tags=["categorias"])

SessionDep = Annotated[Session, Depends(get_session)]


def get_categoria_service(session: SessionDep) -> CategoriaService:
    return CategoriaService(session)


CategoriaServiceDep = Annotated[CategoriaService, Depends(get_categoria_service)]


@router.get("/", response_model=list[Categoria])
def get_categorias(
    service: CategoriaServiceDep,
    nombre: Annotated[Optional[str], Query(max_length=50)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10
):
    return service.get_all(nombre, offset, limit)


@router.get("/{categoria_id}", response_model=Categoria)
def get_categoria(
    categoria_id: int,
    service: CategoriaServiceDep
):
    return service.get_by_id(categoria_id)


@router.post("/", response_model=Categoria, status_code=201)
def crear_categoria(
    categoria: Categoria,
    service: CategoriaServiceDep
):
    return service.create(categoria)


@router.put("/{categoria_id}", response_model=Categoria)
def editar_categoria(
    categoria_id: int,
    datos: Categoria,
    service: CategoriaServiceDep
):
    return service.update(categoria_id, datos)


@router.delete("/{categoria_id}", status_code=204)
def eliminar_categoria(
    categoria_id: int,
    service: CategoriaServiceDep
):
    service.delete(categoria_id)


@router.get("/{categoria_id}/en-uso")
def verificar_categoria_en_uso(
    categoria_id: int,
    service: CategoriaServiceDep
):
    return service.esta_en_uso(categoria_id)