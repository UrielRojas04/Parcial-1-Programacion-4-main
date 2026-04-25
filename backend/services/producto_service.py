"""
SERVICE: ProductoService
========================

PROPÓSITO:
- Lógica de negocio para productos
- MÁS COMPLEJO que Categoría e Ingrediente porque:
  * Maneja relación 1:N con Categoría
  * Maneja relación N:N con Ingredientes
  * Tiene validaciones adicionales para la relación N:N

MÉTODOS CRUD:
- get_all(nombre, categoria_id, offset, limit)
- get_by_id(id)
- create(producto)
- update(id, datos)
- delete(id)

MÉTODOS DE RELACIÓN N:N:
- get_ingredientes(producto_id)
- agregar_ingrediente(producto_id, datos)
- quitar_ingrediente(producto_id, ingrediente_id)

CONCEPTOS NUEVOS:
1. refresh() en relaciones lazy-loaded
2. find_by_producto_e_ingrediente() para prevenir duplicados
3. Validación de combinaciones únicas
"""

from fastapi import HTTPException
from sqlmodel import Session, select
from models.producto import Producto
from models.producto_ingrediente import ProductoIngrediente
from schemas import ProductoIngredienteCreate
from uow import UnitOfWork


class ProductoService:

    def __init__(self, session: Session):
        """Constructor: inicializa UnitOfWork"""
        self.uow = UnitOfWork(session)

    def get_all(self, nombre=None, categoria_id=None, offset=0, limit=10):
        """
        OBTENER TODOS LOS PRODUCTOS (CON FILTROS)
        
        PARÁMETROS:
        - nombre: filtro optional por nombre (contains)
        - categoria_id: filtro optional por categoría
        - offset, limit: paginación
        
        FLUJO:
        1. Construye statement SELECT base
        2. Si nombre != None → agrega WHERE nombre contains
        3. Si categoria_id != None → agrega WHERE categoria_id ==
        4. Aplica paginación (offset + limit)
        5. Ejecuta query en BD
        6. Para cada producto, carga relación N:N (lazy-loaded)
        
        ¿POR QUÉ refresh()?
        - ingrediente_links es una relación lazy-loaded
        - No se carga automáticamente al obtener el producto
        - El acceso a _ = producto.ingrediente_links los carga
        - Refresh sincroniza el objeto con la BD
        
        EJEMPLOS:
        service.get_all()  # todos
        service.get_all(nombre="Torta")  # contiene "Torta"
        service.get_all(categoria_id=2)  # de categoría 2
        service.get_all(nombre="Torta", categoria_id=2)  # combinado
        
        RETORNA:
        List[Producto] con ingrediente_links cargados
        """
        statement = select(Producto)
        if nombre:
            # WHERE nombre CONTAINS nombre
            statement = statement.where(Producto.nombre.contains(nombre))
        if categoria_id:
            # WHERE categoria_id == categoria_id
            statement = statement.where(Producto.categoria_id == categoria_id)
        # LIMIT offset, limit
        statement = statement.offset(offset).limit(limit)
        productos = self.uow.session.exec(statement).all()
        
        # Carga las relaciones N:N para cada producto
        for producto in productos:
            self.uow.session.refresh(producto)
            _ = producto.ingrediente_links  # Acceso lazy-load
        
        return productos

    def get_by_id(self, producto_id: int) -> Producto:
        """
        OBTENER UN PRODUCTO POR ID
        
        PARÁMETRO:
        - producto_id: ID del producto
        
        FLUJO:
        1. Obtiene producto por PK
        2. Si no existe → HTTPException 404
        3. Recarga (para relaciones lazy)
        4. Accede a ingrediente_links (fuerza carga)
        
        RETORNA:
        Producto con ingrediente_links cargados
        
        ERRORES:
        HTTPException(404, "Producto no encontrado")
        """
        producto = self.uow.session.get(Producto, producto_id)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        self.uow.session.refresh(producto)
        _ = producto.ingrediente_links
        
        return producto

    def create(self, producto: Producto) -> Producto:
        """
        CREAR UN NUEVO PRODUCTO
        
        PARÁMETRO:
        - producto: objeto Producto (sin id)
        
        FLUJO:
        1. Inserta en BD
        2. Confirma transacción
        3. Recarga para obtener id y relaciones
        
        RETORNA:
        Producto con id asignado e ingrediente_links cargados
        """
        producto = self.uow.productos.create(producto)
        self.uow.commit()
        self.uow.session.refresh(producto)
        return producto

    def update(self, producto_id: int, datos: Producto) -> Producto:
        """
        ACTUALIZAR UN PRODUCTO
        
        PARÁMETROS:
        - producto_id: ID a editar
        - datos: nuevos valores
        
        FLUJO:
        1. Valida que exista (get_by_id)
        2. Actualiza atributos básicos
        3. NO edita ingredientes aquí (hay método separado)
        4. Persiste en BD
        5. Recarga relaciones
        
        RETORNA:
        Producto actualizado
        """
        producto = self.get_by_id(producto_id)
        producto.nombre = datos.nombre
        producto.precio = datos.precio
        producto.descripcion = datos.descripcion
        producto.categoria_id = datos.categoria_id
        producto = self.uow.productos.update(producto)
        self.uow.commit()
        self.uow.session.refresh(producto)
        return producto

    def delete(self, producto_id: int) -> None:
        """
        ELIMINAR UN PRODUCTO
        
        PARÁMETRO:
        - producto_id: ID a borrar
        
        FLUJO:
        1. Valida existencia
        2. Elimina de BD
        3. Confirma
        4. Si hay CASCADE en FK → ProductoIngrediente también se elimina
        
        RETORNA:
        None
        """
        self.get_by_id(producto_id)
        self.uow.productos.delete(producto_id)
        self.uow.commit()

    def agregar_ingrediente(
        self, producto_id: int, datos: ProductoIngredienteCreate
    ) -> ProductoIngrediente:
        """
        AGREGAR UN INGREDIENTE A UN PRODUCTO (Relación N:N)
        
        PARÁMETROS:
        - producto_id: ID del producto
        - datos: {ingrediente_id: int, cantidad: float}
        
        FLUJO:
        1. Valida que el producto exista
        2. Verifica que NO exista una combinación duplicada
           → Si ya existe → HTTPException 400
           → Previene: mismo ingrediente en el mismo producto 2+ veces
        3. Crea objeto ProductoIngrediente
        4. Inserta en BD
        5. Confirma
        6. Recarga relación
        
        EJEMPLO REQUEST:
        POST /productos/1/ingredientes/
        {
            "ingrediente_id": 5,
            "cantidad": 500
        }
        
        VALIDACIONES:
        - Producto debe existir
        - Ingrediente debe existir (validación en BD)
        - (producto_id, ingrediente_id) debe ser única
        
        RETORNA:
        ProductoIngrediente
        
        ERRORES:
        - HTTPException 404 si producto no existe
        - HTTPException 400 si ya existe la combinación
        """
        self.get_by_id(producto_id)

        # Previene duplicados: busca si ya existe esta combinación
        existente = self.uow.producto_ingredientes.find_by_producto_e_ingrediente(
            producto_id, datos.ingrediente_id
        )
        if existente:
            # Ya existe: rechaza con 400 Bad Request
            raise HTTPException(
                status_code=400, 
                detail="El ingrediente ya está en el producto"
            )

        # Crea la relación
        link = ProductoIngrediente(
            producto_id=producto_id,
            ingrediente_id=datos.ingrediente_id,
            cantidad=datos.cantidad
        )
        self.uow.producto_ingredientes.create(link)
        self.uow.commit()
        self.uow.session.refresh(link)
        return link
    
    def get_ingredientes(self, producto_id: int):
        """
        OBTENER INGREDIENTES DE UN PRODUCTO
        
        PARÁMETRO:
        - producto_id: ID del producto
        
        FLUJO:
        1. Valida que el producto exista
        2. Construye SELECT de ProductoIngrediente filtrando por producto_id
        3. Ejecuta query
        
        RETORNA:
        List[ProductoIngrediente] = lista de vínculos con cantidades
        
        NOTA:
        - Devuelve ProductoIngrediente, no Ingrediente directamente
        - Para obtener el nombre del ingrediente: 
          link.ingrediente.nombre
        """
        self.get_by_id(producto_id)  
        statement = select(ProductoIngrediente).where(
            ProductoIngrediente.producto_id == producto_id
        )
        return self.uow.session.exec(statement).all()

    def quitar_ingrediente(self, producto_id: int, ingrediente_id: int) -> None:
        """
        QUITAR UN INGREDIENTE DE UN PRODUCTO
        
        PARÁMETROS:
        - producto_id: ID del producto
        - ingrediente_id: ID del ingrediente a quitar
        
        FLUJO:
        1. Busca la relación (producto_id, ingrediente_id)
        2. Si no existe → HTTPException 404
        3. Elimina de BD
        4. Confirma
        
        EJEMPLO:
        DELETE /productos/1/ingredientes/5
        → elimina ingrediente 5 del producto 1
        
        RETORNA:
        None
        
        ERRORES:
        HTTPException 404 si la relación no existe
        """
        link = self.uow.producto_ingredientes.find_by_producto_e_ingrediente(
            producto_id, ingrediente_id
        )
        if not link:
            raise HTTPException(
                status_code=404, 
                detail="Relación no encontrada"
            )
        self.uow.session.delete(link)
        self.uow.commit()