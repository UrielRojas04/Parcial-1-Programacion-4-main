from .categoria import Categoria
from .producto import Producto
from .ingrediente import Ingrediente
from .producto_ingrediente import ProductoIngrediente

Categoria.model_rebuild()
Producto.model_rebuild()
Ingrediente.model_rebuild()
ProductoIngrediente.model_rebuild()