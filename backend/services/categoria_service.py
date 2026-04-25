"""
SERVICE: CategoriaService
=========================

PROPÓSITO:
- Contiene TODA la lógica de negocio para categorías
- Los routers llaman aquí, no directamente a la BD

RESPONSABILIDADES:
1. Validaciones de negocio (ej: existe la categoría?)
2. Manejo de errores (HTTPException)
3. Transacciones (commit/rollback)
4. Refresh de relaciones lazy-loaded

PATRÓN:
- get_* = lectura
- create/update/delete = escritura (requieren commit)
- Siempre verifica existencia antes de operar

DIFERENCIA CON ROUTERS:
- Routers = entrada/salida HTTP (qué datos reciben/devuelven)
- Services = lógica pura (validaciones, transacciones, decisiones)
"""

from fastapi import HTTPException
from sqlmodel import Session
from models.categoria import Categoria
from uow import UnitOfWork


class CategoriaService:
    """Servicio de lógica de negocio para Categorias"""
    
    def __init__(self, session: Session):
        """
        CONSTRUCTOR
        session: conexión a la BD inyectada por FastAPI
        self.uow: Unit of Work (agrupa todos los repositorios)
        """
        self.uow = UnitOfWork(session)
    
    def get_all(self, nombre: str | None = None, offset: int = 0, limit: int = 10) -> list[Categoria]:
        """
        OBTENER TODAS LAS CATEGORÍAS
        
        PARÁMETROS:
        - nombre: filtro opcional por nombre (búsqueda contains)
        - offset: desde dónde empezar (paginación)
        - limit: cuántos obtener (paginación)
        
        FLUJO:
        1. Si nombre != None → usa find_by_nombre() (búsqueda)
        2. Si nombre == None → usa get_all() (lista completa)
        3. Aplica paginación con offset:offset+limit
        
        EJEMPLO:
        service.get_all(nombre="Postres", offset=0, limit=10)
        → Busca categorías con "Postres", primeras 10
        
        RETORNA:
        List[Categoria] = lista de objetos Categoria
        """
        if nombre:
            # Si hay filtro, busca por nombre y aplica paginación en Python
            return self.uow.categorias.find_by_nombre(nombre)[offset:offset + limit]
        # Si no hay filtro, trae directamente con paginación en SQL
        return self.uow.categorias.get_all(offset, limit)
    
    def get_by_id(self, categoria_id: int) -> Categoria:
        """
        OBTENER UNA CATEGORÍA POR ID
        
        PARÁMETRO:
        - categoria_id: ID de la categoría
        
        FLUJO:
        1. Intenta obtener la categoría con ese ID
        2. Si NO existe → lanza HTTPException (404)
        3. Si existe → retorna la categoría
        
        EJEMPLO:
        categoria = service.get_by_id(5)
        
        ERRORES:
        HTTPException(status_code=404, detail="Categoria no encontrada")
        → Si no existe, devuelve 404 Not Found al cliente
        
        RETORNA:
        Categoria = objeto con id, nombre, descripcion
        """
        categoria = self.uow.categorias.get_by_id(categoria_id)
        if not categoria:
            # Patrón: siempre validar existencia antes de operar
            raise HTTPException(status_code=404, detail="Categoria no encontrada")
        return categoria
    
    def create(self, categoria: Categoria) -> Categoria:
        """
        CREAR UNA NUEVA CATEGORÍA
        
        PARÁMETRO:
        - categoria: objeto Categoria (sin id, será generado)
        
        FLUJO:
        1. Llama al repositorio para insertar en BD
        2. Flush() = prepara el INSERT sin confirmar aún
        3. Commit() = confirma la transacción
        4. Refresh() = recarga el objeto para obtener el id generado
        
        EJEMPLO:
        cat = Categoria(nombre="Postres", descripcion="...")
        resultado = service.create(cat)
        print(resultado.id)  # 5 (generado por BD)
        
        RETORNA:
        Categoria = objeto con id ya asignado por la BD
        
        ¿POR QUÉ REFRESH?
        - La BD genera automáticamente el id
        - Refresh() sincroniza el objeto en Python con los datos reales
        """
        categoria = self.uow.categorias.create(categoria)
        self.uow.commit()  # Persiste en BD
        self.uow.session.refresh(categoria)  # Recarga id generado
        return categoria
    
    def update(self, categoria_id: int, datos: Categoria) -> Categoria:
        """
        ACTUALIZAR UNA CATEGORÍA EXISTENTE
        
        PARÁMETROS:
        - categoria_id: ID de la categoría a editar
        - datos: objeto Categoria con nuevos valores
        
        FLUJO:
        1. Verifica que la categoría exista (get_by_id)
        2. Modifica los atributos
        3. Persiste cambios (update + commit)
        4. Recarga el objeto (refresh)
        
        EJEMPLO:
        datos = Categoria(nombre="Postres Finos", descripcion="...")
        resultado = service.update(5, datos)
        
        RETORNA:
        Categoria = objeto actualizado
        
        ERRORES:
        - Si categoria_id no existe → HTTPException 404 (del get_by_id)
        """
        categoria = self.get_by_id(categoria_id)  # Valida existencia
        # Actualiza atributos
        categoria.nombre = datos.nombre
        categoria.descripcion = datos.descripcion
        # Persiste en BD
        categoria = self.uow.categorias.update(categoria)
        self.uow.commit()
        self.uow.session.refresh(categoria)
        return categoria
    
    def delete(self, categoria_id: int) -> None:
        """
        ELIMINAR UNA CATEGORÍA
        
        PARÁMETRO:
        - categoria_id: ID de la categoría a borrar
        
        FLUJO:
        1. Verifica que exista (get_by_id)
        2. Elimina de BD
        3. Confirma la transacción
        
        EJEMPLO:
        service.delete(5)
        # Categoría id=5 se elimina de la BD
        
        RETORNA:
        None (no devuelve nada)
        
        ERRORES:
        - Si no existe → HTTPException 404 (del get_by_id)
        
        ¿QUÉ PASA CON LOS PRODUCTOS?
        - Depende del CASCADE en la FK
        - Si hay CASCADE DELETE → se eliminan productos huérfanos
        - Si hay RESTRICT → falla si hay productos en esta categoría
        """
        self.get_by_id(categoria_id)  # Valida existencia
        self.uow.categorias.delete(categoria_id)  # Elimina
        self.uow.commit()  # Confirma
