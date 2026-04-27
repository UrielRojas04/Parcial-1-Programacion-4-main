from typing import Optional
from sqlmodel import SQLModel, Field


class CategoriaBase(SQLModel):
    nombre: str = Field(min_length=2, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=200)
    parent_id: Optional[int] = Field(default=None)


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaRead(CategoriaBase):
    id: int


class CategoriaUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=50)
    descripcion: Optional[str] = Field(default=None, max_length=200)
    parent_id: Optional[int] = Field(default=None)


class IngredienteBase(SQLModel):
    nombre: str = Field(min_length=2, max_length=50)
    unidad: str = Field(max_length=20)


class IngredienteCreate(IngredienteBase):
    pass


class IngredienteRead(IngredienteBase):
    id: int


class IngredienteUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=50)
    unidad: Optional[str] = Field(default=None, max_length=20)


class ProductoBase(SQLModel):
    nombre: str = Field(min_length=2, max_length=100)
    precio: float = Field(gt=0)
    descripcion: Optional[str] = Field(default=None, max_length=300)
    categoria_id: Optional[int] = Field(default=None)


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=100)
    precio: Optional[float] = Field(default=None, gt=0)
    descripcion: Optional[str] = Field(default=None, max_length=300)
    categoria_id: Optional[int] = Field(default=None)


class ProductoIngredienteBase(SQLModel):
    ingrediente_id: int
    cantidad: float = Field(gt=0)


class ProductoIngredienteCreate(ProductoIngredienteBase):
    pass


class ProductoIngredienteRead(ProductoIngredienteBase):
    pass


class ProductoIngredienteUpdate(SQLModel):
    cantidad: Optional[float] = Field(default=None, gt=0)


class ProductoRead(ProductoBase):
    id: int
    ingrediente_links: list[ProductoIngredienteRead] = []