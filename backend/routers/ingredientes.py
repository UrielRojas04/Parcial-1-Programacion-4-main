from fastapi import APIRouter, Depends, Query
from typing import Annotated, Optional
from sqlmodel import Session
from database import get_session
from models.ingrediente import Ingrediente
from services.ingrediente_service import IngredienteService

router = APIRouter(prefix="/ingredientes", tags=["Ingredientes"])

SessionDep = Annotated[Session, Depends(get_session)]


def get_ingrediente_service(session: SessionDep) -> IngredienteService:
    return IngredienteService(session)


IngredienteServiceDep = Annotated[IngredienteService, Depends(get_ingrediente_service)]


@router.get("/", response_model=list[Ingrediente])
def get_ingredientes(
    service: IngredienteServiceDep,
    nombre: Annotated[Optional[str], Query(max_length=50)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return service.get_all(nombre, offset, limit)


@router.get("/{ingrediente_id}", response_model=Ingrediente)
def get_ingrediente(ingrediente_id: int, service: IngredienteServiceDep):
    return service.get_by_id(ingrediente_id)


@router.post("/", response_model=Ingrediente, status_code=201)
def crear_ingrediente(ingrediente: Ingrediente, service: IngredienteServiceDep):
    return service.create(ingrediente)


@router.put("/{ingrediente_id}", response_model=Ingrediente)
def editar_ingrediente(ingrediente_id: int, datos: Ingrediente, service: IngredienteServiceDep):
    return service.update(ingrediente_id, datos)


@router.delete("/{ingrediente_id}", status_code=204)
def eliminar_ingrediente(ingrediente_id: int, service: IngredienteServiceDep):
    service.delete(ingrediente_id)


@router.get("/{ingrediente_id}/en-uso")
def verificar_ingrediente_en_uso(
    ingrediente_id: int,
    service: IngredienteServiceDep
):
    return service.esta_en_uso(ingrediente_id)