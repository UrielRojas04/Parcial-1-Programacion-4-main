"""
ROUTER: Productos
=================

PROPÓSITO:
- Define ENDPOINTS para operaciones de productos
- Más complejo que categorías e ingredientes porque:
  * Tiene relación 1:N con Categoría
  * Tiene relación N:N con Ingredientes

ENDPOINTS CRUD:
- GET /productos/               → listar todos (con filtros)
- GET /productos/{id}           → obtener uno con ingredientes
- POST /productos/              → crear
- PUT /productos/{id}           → editar
- DELETE /productos/{id}        → eliminar

ENDPOINTS DE RELACIÓN N:N:
- GET /productos/{id}/ingredientes/              → listar ingredientes del producto
- POST /productos/{id}/ingredientes/             → agregar ingrediente al producto
- DELETE /productos/{id}/ingredientes/{ing_id}/  → quitar ingrediente

CONCEPTOS NUEVOS AQUÍ:
1. Filtros por categoría: ?categoria_id=2
2. Filtros por nombre: ?nombre=Chocolate
3. Endpoints para gestionar la relación N:N
4. refresh(): cargar relaciones lazy-loaded
"""

from fastapi import APIRouter, Depends, Query
from typing import Annotated, Optional
from sqlmodel import Session
from database import get_session
from models.producto import Producto
from schemas import ProductoCreate, ProductoIngredienteCreate, ProductoRead
from services.producto_service import ProductoService

router = APIRouter(prefix="/productos", tags=["Productos"])

SessionDep = Annotated[Session, Depends(get_session)]


def get_producto_service(session: SessionDep) -> ProductoService:
    """Dependencia que proporciona el servicio de productos"""
    return ProductoService(session)


ProductoServiceDep = Annotated[ProductoService, Depends(get_producto_service)]


# ========== CRUD BÁSICO ==========

@router.get("/", response_model=list[ProductoRead])
def get_productos(
    service: ProductoServiceDep,
    
    # Filtro por nombre: /productos/?nombre=Torta
    nombre: Annotated[Optional[str], Query(max_length=100)] = None,
    
    # Filtro por categoría: /productos/?categoria_id=2
    # ge=1 = mayor o igual a 1 (debe ser válido si se envía)
    categoria_id: Annotated[Optional[int], Query(ge=1)] = None,
    
    # Paginación: desde dónde empezar
    offset: Annotated[int, Query(ge=0)] = 0,
    
    # Paginación: cuántos trae (máx 100)
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    """
    Obtiene una lista de productos con filtros y paginación
    
    EJEMPLOS:
    GET /productos/                                  → todos (primeros 10)
    GET /productos/?nombre=Torta                     → contiene "Torta"
    GET /productos/?categoria_id=2                   → de categoría 2
    GET /productos/?nombre=Torta&categoria_id=2      → combinado
    GET /productos/?offset=20&limit=5                → registros 20-25
    """
    return service.get_all(nombre, categoria_id, offset, limit)


@router.get("/{producto_id}", response_model=ProductoRead)
def get_producto(producto_id: int, service: ProductoServiceDep):
    """
    Obtiene un producto con todos sus detalles e ingredientes
    
    EJEMPLO RESPUESTA:
    {
        "id": 1,
        "nombre": "Torta de Chocolate",
        "precio": 15.50,
        "descripcion": "Torta casera",
        "categoria_id": 2,
        "ingrediente_links": [
            {"ingrediente_id": 5, "cantidad": 500},    # 500g de Harina
            {"ingrediente_id": 3, "cantidad": 12}      # 12 Huevos
        ]
    }
    """
    return service.get_by_id(producto_id)


@router.post("/", response_model=ProductoRead, status_code=201)
def crear_producto(producto: Producto, service: ProductoServiceDep):
    """
    Crea un nuevo producto
    
    REQUEST:
    POST /productos/
    {
        "nombre": "Torta de Chocolate",
        "precio": 15.50,
        "descripcion": "Torta casera de chocolate",
        "categoria_id": 2
    }
    
    RESPUESTA (201 Created):
    {
        "id": 1,  ← generado por BD
        "nombre": "Torta de Chocolate",
        "precio": 15.50,
        "descripcion": "Torta casera de chocolate",
        "categoria_id": 2,
        "ingrediente_links": []  ← vacío al crear, se agregan después
    }
    
    VALIDACIONES:
    - nombre: min 2, max 100
    - precio: must be > 0
    - categoria_id: si se envía, debe existir (validación en BD)
    """
    return service.create(producto)


@router.put("/{producto_id}", response_model=ProductoRead)
def editar_producto(producto_id: int, datos: Producto, service: ProductoServiceDep):
    """
    Edita un producto existente
    
    REQUEST:
    PUT /productos/1
    {
        "nombre": "Torta de Chocolate Premium",
        "precio": 25.00,
        "descripcion": "Torta de chocolate 70%",
        "categoria_id": 2
    }
    
    NOTA:
    - No edita ingredientes aquí (eso es en endpoints separados)
    - Solo edita datos básicos
    """
    return service.update(producto_id, datos)


@router.delete("/{producto_id}", status_code=204)
def eliminar_producto(producto_id: int, service: ProductoServiceDep):
    """
    Elimina un producto
    
    REQUEST:
    DELETE /productos/1
    
    NOTA:
    - Al eliminar un producto, se eliminan automáticamente
      sus ingredientes en la tabla ProductoIngrediente
      (por CASCADE en la foreign key)
    """
    service.delete(producto_id)


# ========== RELACIÓN N:N: INGREDIENTES ==========

@router.get("/{producto_id}/ingredientes")
def get_ingredientes_producto(producto_id: int, service: ProductoServiceDep):
    """
    Obtiene la lista de ingredientes de un producto
    
    EJEMPLO:
    GET /productos/1/ingredientes
    
    RESPUESTA:
    [
        {
            "producto_id": 1,
            "ingrediente_id": 5,
            "cantidad": 500  ← 500 gramos de Harina
        },
        {
            "producto_id": 1,
            "ingrediente_id": 3,
            "cantidad": 12   ← 12 unidades de Huevo
        }
    ]
    
    NOTA:
    - Esto devuelve ProductoIngrediente, no Ingrediente directamente
    - Si querés el nombre del ingrediente, necesitás hacer otra query
    - Por eso ProductoRead incluye ingrediente_links expandido
    """
    return service.get_ingredientes(producto_id)


@router.post("/{producto_id}/ingredientes", status_code=201)
def agregar_ingrediente(
    producto_id: int,
    datos: ProductoIngredienteCreate,
    service: ProductoServiceDep
):
    """
    Agrega un ingrediente a un producto
    
    REQUEST:
    POST /productos/1/ingredientes
    {
        "ingrediente_id": 5,
        "cantidad": 500
    }
    
    SIGNIFICADO:
    "Agrega el ingrediente id=5 (Harina) al producto id=1,
    en cantidad 500 (gramos)"
    
    RESPUESTA (201 Created):
    {
        "producto_id": 1,
        "ingrediente_id": 5,
        "cantidad": 500
    }
    
    VALIDACIONES:
    - Producto debe existir (sino → 404)
    - Ingrediente debe existir (sino → error en BD)
    - No puede haber duplicados: si ya existe esta combinación → 400 Bad Request
    """
    return service.agregar_ingrediente(producto_id, datos)


@router.delete("/{producto_id}/ingredientes/{ingrediente_id}", status_code=204)
def quitar_ingrediente(
    producto_id: int,
    ingrediente_id: int,
    service: ProductoServiceDep
):
    """
    Quita un ingrediente de un producto
    
    REQUEST:
    DELETE /productos/1/ingredientes/5
    
    SIGNIFICADO:
    "Elimina el ingrediente id=5 del producto id=1"
    
    RESPUESTA:
    (vacía, solo 204 No Content)
    
    VALIDACIONES:
    - Producto debe existir
    - Relación (producto, ingrediente) debe existir (sino → 404)
    """
    service.quitar_ingrediente(producto_id, ingrediente_id)