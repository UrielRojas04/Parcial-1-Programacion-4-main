from typing import Optional
from sqlmodel import SQLModel, Field


class CategoriaCreate(SQLModel):
    nombre: str = Field(min_length=2, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=200)


class IngredienteCreate(SQLModel):
    nombre: str = Field(min_length=2, max_length=50)
    unidad: str = Field(max_length=20)


class ProductoCreate(SQLModel):
    nombre: str = Field(min_length=2, max_length=100)
    precio: float = Field(gt=0)
    descripcion: Optional[str] = Field(default=None, max_length=300)
    categoria_id: Optional[int] = Field(default=None)


class ProductoIngredienteCreate(SQLModel):
    ingrediente_id: int
    cantidad: float = Field(gt=0)


class ProductoIngredienteRead(SQLModel):
    ingrediente_id: int
    cantidad: float = Field(gt=0)


class ProductoRead(SQLModel):
    id: int
    nombre: str
    precio: float
    descripcion: Optional[str] = None
    categoria_id: Optional[int] = None
    ingrediente_links: list[ProductoIngredienteRead] = []