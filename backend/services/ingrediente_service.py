"""
SERVICE: IngredienteService
==========================

PROPÓSITO:
- Lógica de negocio para ingredientes
- Estructura idéntica a CategoriaService (patrón CRUD)

MÉTODOS:
- get_all() = lista con filtro opcional
- get_by_id() = obtiene uno o 404
- create() = inserta y confirma
- update() = modifica y confirma
- delete() = elimina y confirma

PATRÓN UNIVERSAL:
1. Validar (¿existe?)
2. Operar (crear/editar/eliminar)
3. Persistir (commit)
4. Refrescar (refresh para relaciones lazy)
"""

from fastapi import HTTPException
from sqlmodel import Session, select, func
from models.ingrediente import Ingrediente
from models.producto_ingrediente import ProductoIngrediente
from uow import UnitOfWork


class IngredienteService:
    """Servicio de lógica de negocio para Ingredientes"""
    
    def __init__(self, session: Session):
        """Constructor: inicializa UnitOfWork con la sesión"""
        self.uow = UnitOfWork(session)
    
    def get_all(self, nombre: str | None = None, offset: int = 0, limit: int = 10) -> list[Ingrediente]:
        """
        OBTENER TODOS LOS INGREDIENTES
        
        PARÁMETROS:
        - nombre: filtro opcional (búsqueda contains)
        - offset: paginación desde
        - limit: paginación cuántos
        
        EJEMPLO:
        service.get_all(nombre="Harina", offset=0, limit=10)
        
        RETORNA:
        List[Ingrediente]
        """
        if nombre:
            return self.uow.ingredientes.find_by_nombre(nombre)[offset:offset + limit]
        return self.uow.ingredientes.get_all(offset, limit)
    
    def get_by_id(self, ingrediente_id: int) -> Ingrediente:
        """
        OBTENER UN INGREDIENTE POR ID
        
        PARÁMETRO:
        - ingrediente_id: ID del ingrediente
        
        FLUJO:
        1. Busca en BD
        2. Si no existe → HTTPException 404
        
        RETORNA:
        Ingrediente
        """
        ingrediente = self.uow.ingredientes.get_by_id(ingrediente_id)
        if not ingrediente:
            raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
        return ingrediente
    
    def create(self, ingrediente: Ingrediente) -> Ingrediente:
        """
        CREAR UN NUEVO INGREDIENTE
        
        PARÁMETRO:
        - ingrediente: objeto Ingrediente (sin id)
        
        FLUJO:
        1. Inserta en BD
        2. Confirma transacción
        3. Recarga para obtener id generado
        
        EJEMPLO:
        ing = Ingrediente(nombre="Harina", unidad="gramos")
        resultado = service.create(ing)
        print(resultado.id)  # 3
        
        RETORNA:
        Ingrediente con id asignado
        """
        ingrediente = self.uow.ingredientes.create(ingrediente)
        self.uow.commit()
        self.uow.session.refresh(ingrediente)
        return ingrediente
    
    def update(self, ingrediente_id: int, datos: Ingrediente) -> Ingrediente:
        """
        ACTUALIZAR UN INGREDIENTE
        
        PARÁMETROS:
        - ingrediente_id: ID a editar
        - datos: nuevos valores
        
        FLUJO:
        1. Verifica que exista
        2. Actualiza atributos
        3. Persiste en BD
        4. Recarga objeto
        
        RETORNA:
        Ingrediente actualizado
        """
        ingrediente = self.get_by_id(ingrediente_id)
        ingrediente.nombre = datos.nombre
        ingrediente.unidad = datos.unidad
        ingrediente = self.uow.ingredientes.update(ingrediente)
        self.uow.commit()
        self.uow.session.refresh(ingrediente)
        return ingrediente
    
    def delete(self, ingrediente_id: int) -> None:
        """
        ELIMINAR UN INGREDIENTE
        
        PARÁMETRO:
        - ingrediente_id: ID a borrar
        
        FLUJO:
        1. Verifica existencia
        2. Elimina de BD
        3. Confirma
        
        NOTA:
        - Si hay productos que usan este ingrediente, depende del CASCADE
        """
        self.get_by_id(ingrediente_id)
        self.uow.ingredientes.delete(ingrediente_id)
        self.uow.commit()

    def esta_en_uso(self, ingrediente_id: int) -> dict:
        """
        VERIFICAR SI UN INGREDIENTE ESTÁ EN USO
        
        PARÁMETRO:
        - ingrediente_id: ID del ingrediente
        
        FLUJO:
        1. Verifica que el ingrediente exista
        2. Cuenta cuántos productos lo usan
        
        RETORNA:
        {"en_uso": bool, "cantidad": int}
        """
        # Verificar que el ingrediente exista
        self.get_by_id(ingrediente_id)
        
        # Contar productos que usan este ingrediente
        statement = select(func.count()).select_from(ProductoIngrediente).where(
            ProductoIngrediente.ingrediente_id == ingrediente_id
        )
        cantidad = self.uow.session.exec(statement).one()
        
        return {
            "en_uso": cantidad > 0,
            "cantidad": cantidad
        }
