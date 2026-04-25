"""
ROUTER: Categorías
==================

PROPÓSITO:
- Define todos los ENDPOINTS para operaciones de categorías
- Recibe requests HTTP, inyecta dependencias, devuelve respuestas
- NO contiene lógica de negocio (eso es responsabilidad del Service)

CONCEPTOS IMPORTANTES:
1. APIRouter = agrupa endpoints relacionados bajo un prefijo
2. @router.get, @router.post, etc. = decoradores que definen el método HTTP
3. Annotated[Type, Constraint] = tipado fuerte con validación automática
4. Dependencia injection = FastAPI inyecta el Service automáticamente
5. response_model = especifica qué schema devuelve el endpoint

ENDPOINTS:
- GET /categorias/               → listar todas (con filtros opcionales)
- GET /categorias/{id}           → obtener una
- POST /categorias/              → crear (status_code=201)
- PUT /categorias/{id}           → editar
- DELETE /categorias/{id}        → eliminar (status_code=204)

FLUJO TÍPICO:
1. Cliente → GET /categorias/?nombre=Postres&limit=10
2. FastAPI valida parámetros con Annotated
3. Inyecta el Service
4. Service ejecuta lógica de negocio
5. Router devuelve respuesta formateada
"""

from fastapi import APIRouter, Depends, Query
from typing import Annotated, Optional
from sqlmodel import Session
from database import get_session
from models.categoria import Categoria
from services.categoria_service import CategoriaService

# ========== CONFIGURACIÓN DEL ROUTER ==========
# prefix="/categorias" = todos los endpoints empiezan con /categorias
# tags=["categorias"] = agrupa en la documentación Swagger
router = APIRouter(prefix="/categorias", tags=["categorias"])

# ========== DEPENDENCIA INYECTADA: Session ==========
# SessionDep = atajo para "inyecta la sesión de BD"
# Annotated[Session, Depends(get_session)]
#   - Session = tipo que se inyecta
#   - Depends(get_session) = función que proporciona la sesión
#   - Annotated = hace el tipado más explícito
SessionDep = Annotated[Session, Depends(get_session)]


def get_categoria_service(session: SessionDep) -> CategoriaService:
    """
    Dependencia que proporciona el servicio de categorías
    
    FLUJO:
    1. FastAPI inyecta la sesión
    2. Esta función crea el servicio con la sesión
    3. FastAPI inyecta el servicio en los endpoints
    
    ¿POR QUÉ?
    - Centraliza la creación del servicio
    - Facilita testing (podemos mockear el servicio)
    - Sigue el patrón de inyección de dependencias de FastAPI
    """
    return CategoriaService(session)


# ========== DEPENDENCIA INYECTADA: Service ==========
# CategoriaServiceDep = atajo para "inyecta el servicio"
# Los endpoints usan esto en lugar de llamar a get_categoria_service manualmente
CategoriaServiceDep = Annotated[CategoriaService, Depends(get_categoria_service)]


# ========== ENDPOINT 1: LISTAR CATEGORÍAS ==========
@router.get("/", response_model=list[Categoria])
def get_categorias(
    # inyección de dependencia: el servicio
    service: CategoriaServiceDep,
    
    # PARÁMETRO: nombre (query string)
    # Annotated[Optional[str], Query(max_length=50)] = opcional, max 50 caracteres
    # = None = si no lo envían, es None
    # Query(...) = especifica que es un parámetro de query (no body)
    #
    # EJEMPLO:
    # GET /categorias/?nombre=Postres  → busca categorías con "Postres" en el nombre
    # GET /categorias/                 → devuelve todas
    nombre: Annotated[Optional[str], Query(max_length=50)] = None,
    
    # PARÁMETRO: offset (paginación, desde dónde empezar)
    # Query(ge=0) = "greater than or equal 0" → rechaza números negativos
    # = 0 = por defecto empieza desde el primero
    offset: Annotated[int, Query(ge=0)] = 0,
    
    # PARÁMETRO: limit (paginación, cuántos obtener)
    # Query(ge=1, le=100) = entre 1 y 100
    # = 10 = por defecto trae 10 registros
    limit: Annotated[int, Query(ge=1, le=100)] = 10
):
    """
    Obtiene una lista de categorías
    
    EJEMPLOS:
    GET /categorias/                          → primeras 10 categorías
    GET /categorias/?nombre=Postres            → categorías con "Postres", primeras 10
    GET /categorias/?offset=20&limit=5         → categorías 20-25
    GET /categorias/?nombre=Pos&offset=5&limit=3  → combinado
    """
    return service.get_all(nombre, offset, limit)


# ========== ENDPOINT 2: OBTENER UNA CATEGORÍA POR ID ==========
@router.get("/{categoria_id}", response_model=Categoria)
def get_categoria(
    # categoria_id: parámetro de ruta (no query)
    # FastAPI automáticamente lo extrae de la URL: /categorias/5 → categoria_id=5
    categoria_id: int,
    
    # inyección del servicio
    service: CategoriaServiceDep
):
    """
    Obtiene una categoría por su ID
    
    EJEMPLO:
    GET /categorias/5  → devuelve la categoría con id=5
    
    ERROR:
    GET /categorias/999  → si no existe → 404 Not Found
    """
    return service.get_by_id(categoria_id)


# ========== ENDPOINT 3: CREAR CATEGORÍA ==========
@router.post("/", response_model=Categoria, status_code=201)
def crear_categoria(
    # categoria: parámetro de BODY (JSON)
    # FastAPI automáticamente deserializa el JSON en un objeto Categoria
    # Aplica validaciones de CategoriaCreate (si lo usáramos)
    # En este caso acepta el modelo completo Categoria
    categoria: Categoria,
    
    # inyección del servicio
    service: CategoriaServiceDep
):
    """
    Crea una nueva categoría
    
    REQUEST BODY:
    POST /categorias/
    {
        "nombre": "Postres",
        "descripcion": "Toda clase de postres dulces"
    }
    
    RESPUESTA (201 Created):
    {
        "id": 5,  ← generado por BD
        "nombre": "Postres",
        "descripcion": "Toda clase de postres dulces"
    }
    
    VALIDACIONES AUTOMÁTICAS:
    - nombre: min 2, max 50 caracteres → si no cumple → 422 Unprocessable Entity
    - descripcion: max 200 caracteres
    
    STATUS_CODE:
    - status_code=201 = Created (estándar HTTP para "nuevo recurso creado")
    - En lugar de 200 OK que sería genérico
    """
    return service.create(categoria)


# ========== ENDPOINT 4: EDITAR CATEGORÍA ==========
@router.put("/{categoria_id}", response_model=Categoria)
def editar_categoria(
    # categoria_id: parámetro de ruta
    categoria_id: int,
    
    # datos: parámetro de body (JSON con los nuevos datos)
    datos: Categoria,
    
    # inyección del servicio
    service: CategoriaServiceDep
):
    """
    Actualiza una categoría existente
    
    REQUEST:
    PUT /categorias/5
    {
        "nombre": "Postres Premium",
        "descripcion": "Postres de alta gama"
    }
    
    RESPUESTA:
    {
        "id": 5,
        "nombre": "Postres Premium",
        "descripcion": "Postres de alta gama"
    }
    
    ERROR:
    - Si categoria_id no existe → 404 Not Found (del service)
    """
    return service.update(categoria_id, datos)


# ========== ENDPOINT 5: ELIMINAR CATEGORÍA ==========
@router.delete("/{categoria_id}", status_code=204)
def eliminar_categoria(
    # categoria_id: parámetro de ruta
    categoria_id: int,
    
    # inyección del servicio
    service: CategoriaServiceDep
):
    """
    Elimina una categoría
    
    REQUEST:
    DELETE /categorias/5
    
    RESPUESTA:
    (vacía, solo status 204 No Content)
    
    STATUS_CODE:
    - 204 No Content = la operación tuvo éxito pero sin body de respuesta
    - Es el estándar para DELETE
    
    ERROR:
    - Si categoria_id no existe → 404 Not Found (del service)
    """
    service.delete(categoria_id)
