"""
ESQUEMAS: Validación de Requests y Responses
==============================================

DIFERENCIA IMPORTANTE:
1. Models (en models/) = definen la TABLA en BD
2. Schemas (aquí) = validan ENTRADA (requests) y formatean SALIDA (responses)

POR QUÉ SEPARARLOS:
- Un Producto en BD tiene: id, nombre, precio, descripcion, categoria_id, ingrediente_links
- Cuando el FRONTEND crea un producto, NO debe enviar el id (BD lo genera)
- Por eso existe ProductoCreate (sin id) y ProductoRead (con id + relaciones)

PATRÓN:
- CategoriaCreate = Entrada: qué datos requiero para CREAR
- CategoriaRead = Salida: qué datos devuelvo al cliente
- Categoria = Modelo en BD (tiene id, generado automáticamente)

VALIDACIÓN AUTOMÁTICA:
Cada Field(min_length=, max_length=, gt=, etc.) se valida ANTES de llegar al router
Si el cliente envía datos inválidos → FastAPI devuelve 422 Unprocessable Entity
"""

from typing import Optional
from sqlmodel import SQLModel, Field


# ========== ESQUEMAS DE CATEGORÍA ==========

class CategoriaCreate(SQLModel):
    """
    ENTRADA para crear una categoría
    El cliente envía SOLO estos datos
    
    EJEMPLO REQUEST:
    POST /categorias/
    {
        "nombre": "Postres",
        "descripcion": "Toda clase de postres"
    }
    """
    # nombre: obligatorio, 2-50 caracteres
    nombre: str = Field(min_length=2, max_length=50)
    
    # descripcion: opcional, max 200 caracteres
    # Si no lo envían, se guarda como NULL en BD
    descripcion: Optional[str] = Field(default=None, max_length=200)


# ========== ESQUEMAS DE INGREDIENTE ==========

class IngredienteCreate(SQLModel):
    """
    ENTRADA para crear un ingrediente
    El cliente envía SOLO estos datos
    
    EJEMPLO REQUEST:
    POST /ingredientes/
    {
        "nombre": "Harina",
        "unidad": "gramos"
    }
    """
    # nombre: obligatorio, 2-50 caracteres
    nombre: str = Field(min_length=2, max_length=50)
    
    # unidad: obligatorio, max 20 caracteres
    # Ej: "gramos", "ml", "unidades", "tazas"
    unidad: str = Field(max_length=20)


# ========== ESQUEMAS DE PRODUCTO ==========

class ProductoCreate(SQLModel):
    """
    ENTRADA para crear un producto
    El cliente envía SOLO estos datos (sin id, sin ingredientes)
    
    EJEMPLO REQUEST:
    POST /productos/
    {
        "nombre": "Torta de Chocolate",
        "precio": 15.50,
        "descripcion": "Torta casera de chocolate",
        "categoria_id": 2
    }
    """
    # nombre: obligatorio, 2-100 caracteres
    nombre: str = Field(min_length=2, max_length=100)
    
    # precio: obligatorio, must be > 0
    # Field(gt=0) = "greater than zero"
    # Si envían -5 o 0 → error automático
    precio: float = Field(gt=0)
    
    # descripcion: opcional, max 300 caracteres
    descripcion: Optional[str] = Field(default=None, max_length=300)
    
    # categoria_id: opcional, refiere a una categoría existente
    # Si envían un id que no existe en Categorias → error en la BD
    categoria_id: Optional[int] = Field(default=None)


class ProductoIngredienteCreate(SQLModel):
    """
    ENTRADA para agregar un ingrediente a un producto
    
    EJEMPLO REQUEST:
    POST /productos/1/ingredientes/
    {
        "ingrediente_id": 5,
        "cantidad": 500
    }
    
    SIGNIFICADO:
    "Agrega el ingrediente id=5 al producto id=1 en cantidad 500"
    """
    # ingrediente_id: obligatorio, referencia a un Ingrediente
    ingrediente_id: int
    
    # cantidad: obligatorio, must be > 0
    # Ej: 500 (gramos), 12 (unidades), 2.5 (tazas)
    cantidad: float = Field(gt=0)


class ProductoIngredienteRead(SQLModel):
    """
    SALIDA cuando se devuelve un ingrediente dentro de un producto
    (Nota: hay un typo en el nombre "Ingredinennte" en el archivo original)
    
    EJEMPLO RESPONSE en GET /productos/1:
    {
        "id": 1,
        "nombre": "Torta de Chocolate",
        "precio": 15.50,
        "ingrediente_links": [
            {
                "ingrediente_id": 5,
                "cantidad": 500
            },
            {
                "ingrediente_id": 3,
                "cantidad": 12
            }
        ]
    }
    """
    # ingrediente_id: referencia al ingrediente
    ingrediente_id: int
    
    # cantidad: la cantidad específica para este producto
    cantidad: float = Field(gt=0)


class ProductoRead(SQLModel):
    """
    SALIDA cuando se devuelve un producto
    Incluye id (generado por BD) e ingredientes (relación N:N)
    
    EJEMPLO RESPONSE en GET /productos/1:
    {
        "id": 1,
        "nombre": "Torta de Chocolate",
        "precio": 15.50,
        "descripcion": "Torta casera",
        "categoria_id": 2,
        "ingrediente_links": [
            {"ingrediente_id": 5, "cantidad": 500},
            {"ingrediente_id": 3, "cantidad": 12}
        ]
    }
    """
    # id: devuelto por BD, no lo envía el cliente
    id: int
    
    # datos básicos del producto
    nombre: str
    precio: float
    descripcion: Optional[str] = None
    categoria_id: Optional[int] = None
    
    # relación N:N: lista de ingredientes
    # Cada elemento es un ProductoIngredienteRead
    ingrediente_links: list[ProductoIngredienteRead] = []