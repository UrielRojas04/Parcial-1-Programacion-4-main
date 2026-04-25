"""
ROUTER: Ingredientes
====================

PROPÓSITO:
- Define todos los ENDPOINTS para operaciones de ingredientes
- Estructura idéntica a categorias.py (patrón CRUD estándar)

ENDPOINTS:
- GET /ingredientes/               → listar todos
- GET /ingredientes/{id}           → obtener uno
- POST /ingredientes/              → crear
- PUT /ingredientes/{id}           → editar
- DELETE /ingredientes/{id}        → eliminar

DIFERENCIA CON CATEGORÍAS:
- No hay diferencia conceptual
- Mismo patrón de inyección de dependencias
- Mismo manejo de validaciones con Annotated
"""

from fastapi import APIRouter, Depends, Query
from typing import Annotated, Optional
from sqlmodel import Session
from database import get_session
from models.ingrediente import Ingrediente
from services.ingrediente_service import IngredienteService

router = APIRouter(prefix="/ingredientes", tags=["Ingredientes"])

SessionDep = Annotated[Session, Depends(get_session)]


def get_ingrediente_service(session: SessionDep) -> IngredienteService:
    """Dependencia que proporciona el servicio de ingredientes"""
    return IngredienteService(session)


IngredienteServiceDep = Annotated[IngredienteService, Depends(get_ingrediente_service)]


@router.get("/", response_model=list[Ingrediente])
def get_ingredientes(
    service: IngredienteServiceDep,
    # Filtro opcional por nombre: /ingredientes/?nombre=Harina
    nombre: Annotated[Optional[str], Query(max_length=50)] = None,
    # Paginación: offset=0 (desde el primero)
    offset: Annotated[int, Query(ge=0)] = 0,
    # Paginación: limit=10 (trae 10 registros)
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    """
    Obtiene una lista de ingredientes
    
    EJEMPLOS:
    GET /ingredientes/                     → primeros 10
    GET /ingredientes/?nombre=Harina       → contiene "Harina"
    GET /ingredientes/?offset=5&limit=3    → registros 5-8
    """
    return service.get_all(nombre, offset, limit)


@router.get("/{ingrediente_id}", response_model=Ingrediente)
def get_ingrediente(ingrediente_id: int, service: IngredienteServiceDep):
    """
    Obtiene un ingrediente por ID
    
    EJEMPLO:
    GET /ingredientes/3  → devuelve {id: 3, nombre: "Huevo", unidad: "unidades"}
    """
    return service.get_by_id(ingrediente_id)


@router.post("/", response_model=Ingrediente, status_code=201)
def crear_ingrediente(ingrediente: Ingrediente, service: IngredienteServiceDep):
    """
    Crea un nuevo ingrediente
    
    REQUEST:
    POST /ingredientes/
    {
        "nombre": "Harina",
        "unidad": "gramos"
    }
    
    RESPUESTA (201 Created):
    {
        "id": 5,
        "nombre": "Harina",
        "unidad": "gramos"
    }
    
    VALIDACIONES:
    - nombre: min 2, max 50 caracteres
    - unidad: max 20 caracteres
    """
    return service.create(ingrediente)


@router.put("/{ingrediente_id}", response_model=Ingrediente)
def editar_ingrediente(ingrediente_id: int, datos: Ingrediente, service: IngredienteServiceDep):
    """
    Edita un ingrediente existente
    
    REQUEST:
    PUT /ingredientes/3
    {
        "nombre": "Harina de Trigo",
        "unidad": "kilogramos"
    }
    """
    return service.update(ingrediente_id, datos)


@router.delete("/{ingrediente_id}", status_code=204)
def eliminar_ingrediente(ingrediente_id: int, service: IngredienteServiceDep):
    """
    Elimina un ingrediente
    
    REQUEST:
    DELETE /ingredientes/3
    
    RESPUESTA:
    (vacía, solo 204 No Content)
    """
    service.delete(ingrediente_id)


# ========== ENDPOINT 6: VERIFICAR SI INGREDIENTE ESTÁ EN USO ==========
@router.get("/{ingrediente_id}/en-uso")
def verificar_ingrediente_en_uso(
    ingrediente_id: int,
    service: IngredienteServiceDep
):
    """
    Verifica si un ingrediente está en uso (está en productos)
    
    EJEMPLO:
    GET /ingredientes/5/en-uso
    
    RESPUESTA:
    {"en_uso": true, "cantidad": 3}  o  {"en_uso": false, "cantidad": 0}
    """
    return service.esta_en_uso(ingrediente_id)