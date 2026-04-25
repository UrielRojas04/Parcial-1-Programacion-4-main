"""
PATRÓN: Repository (Repositorio)
================================

¿QUÉ ES?
- Clase GENÉRICA que agrupa operaciones CRUD comunes
- Usa TypeVar y Generic para funcionar con cualquier modelo
- Evita repetir código de BD en cada servicio

OPERACIONES BÁSICAS:
- get_by_id(id) → obtiene por clave primaria
- get_all(offset, limit) → lista con paginación
- create(obj) → inserta
- update(obj) → modifica
- delete(id) → elimina

PATRÓN GENÉRICO:
- T = TypeVar = representa "el modelo" (Categoria, Producto, etc.)
- Generic[T] = este repositorio funciona con cualquier tipo T
- self.model = la clase del modelo (Categoria, Producto, etc.)

¿POR QUÉ FUNCIONA?
- Todas las entidades SQLModel comparten misma estructura
- Mismo crear, obtener, actualizar, eliminar
- Solo cambia la entidad (Categoria vs Producto)
"""

from typing import TypeVar, Generic, List, Optional
from sqlmodel import Session, select
from sqlalchemy.orm import DeclarativeBase

# TypeVar: variable que representa "cualquier tipo de modelo"
# bound=DeclarativeBase: solo funciona con SQLModel/SQLAlchemy
T = TypeVar("T", bound=DeclarativeBase)


class BaseRepository(Generic[T]):
    """
    Repositorio base GENÉRICO con operaciones CRUD comunes
    
    USO:
    - class CategoriaRepository(BaseRepository[Categoria])
    - class ProductoRepository(BaseRepository[Producto])
    
    PATRÓN GENÉRICO:
    - T es un placeholder: cuando creas CategoriaRepository,
      T se reemplaza por Categoria
    """
    
    def __init__(self, session: Session, model: type[T]):
        """
        CONSTRUCTOR
        
        PARÁMETROS:
        - session: conexión a la BD (SQLModel Session)
        - model: la clase del modelo (Categoria, Producto, etc.)
        
        EJEMPLO:
        repo = CategoriaRepository(session, Categoria)
        → self.session = session
        → self.model = Categoria
        """
        self.session = session
        self.model = model
    
    def get_by_id(self, id: int) -> Optional[T]:
        """
        OBTENER ENTIDAD POR CLAVE PRIMARIA
        
        PARÁMETRO:
        - id: valor de la PK
        
        FLUJO:
        - session.get(self.model, id)
        - Ej: session.get(Categoria, 5) → obtiene categoría con id=5
        
        RETORNA:
        - T (Categoria, Producto, etc.) si existe
        - None si no existe
        
        EJEMPLO SQL GENERADO:
        SELECT * FROM categoria WHERE id = 5
        """
        return self.session.get(self.model, id)
    
    def get_all(self, offset: int = 0, limit: int = 10) -> List[T]:
        """
        OBTENER TODAS LAS ENTIDADES (con paginación)
        
        PARÁMETROS:
        - offset: desde dónde empezar (0-based)
        - limit: cuántas obtener (máx)
        
        FLUJO:
        1. Construye: SELECT self.model
        2. Agrega: OFFSET offset
        3. Agrega: LIMIT limit
        4. Ejecuta: exec(statement).all()
        
        RETORNA:
        List[T] = lista de entidades
        
        EJEMPLO SQL GENERADO:
        SELECT * FROM categoria OFFSET 0 LIMIT 10
        """
        statement = select(self.model).offset(offset).limit(limit)
        return self.session.exec(statement).all()
    
    def create(self, obj: T) -> T:
        """
        CREAR UNA NUEVA ENTIDAD
        
        PARÁMETRO:
        - obj: instancia del modelo (sin id)
        
        FLUJO:
        1. session.add(obj) → agrega a la sesión
        2. session.flush() → prepara INSERT sin confirmar
        
        ¿POR QUÉ flush() y no commit()?
        - flush() prepara pero no confirma aún
        - El service hace commit() después
        - Permite que el service controle transacciones
        
        RETORNA:
        T = objeto (aún sin id si no es autoincrementable)
        
        NOTA:
        - El id se asigna al commit() o al refresh()
        """
        self.session.add(obj)
        self.session.flush()
        return obj
    
    def update(self, obj: T) -> T:
        """
        ACTUALIZAR UNA ENTIDAD EXISTENTE
        
        PARÁMETRO:
        - obj: instancia con atributos modificados
        
        FLUJO:
        1. session.merge(obj) → sincroniza cambios con sesión
        2. session.flush() → prepara UPDATE sin confirmar
        
        ¿POR QUÉ merge()?
        - El objeto puede venir "detached" (no en la sesión actual)
        - merge() lo reattach y sincroniza los cambios
        
        RETORNA:
        T = objeto sincronizado
        
        EJEMPLO SQL GENERADO:
        UPDATE categoria SET nombre='Postres' WHERE id=5
        """
        self.session.merge(obj)
        self.session.flush()
        return obj
    
    def delete(self, id: int) -> bool:
        """
        ELIMINAR UNA ENTIDAD POR ID
        
        PARÁMETRO:
        - id: valor de la PK
        
        FLUJO:
        1. Obtiene la entidad por ID
        2. Si existe → session.delete(obj) + session.flush()
        3. Si no existe → retorna False
        
        RETORNA:
        - bool: True si se eliminó, False si no existía
        
        EJEMPLO SQL GENERADO:
        DELETE FROM categoria WHERE id = 5
        """
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            self.session.flush()
            return True
        return False
