"""
PATRÓN: Unit of Work (Unidad de Trabajo)
=========================================

¿QUÉ ES?
- Centraliza TODOS los repositorios en un solo objeto
- Gestiona transacciones (commit/rollback)
- Proporciona "punto único de acceso" a la BD

BENEFICIOS:
1. El service solo conoce UnitOfWork, no repositorios individuales
2. Las transacciones se controlan desde un lugar
3. Fácil testear: mockear UoW es suficiente
4. Evita pasar session.commit() en 10 sitios diferentes

ESTRUCTURA:
- UoW agrupa: categorias, ingredientes, productos, producto_ingredientes
- UoW controla: commit(), rollback(), close()

PATRÓN DE USO:
uow = UnitOfWork(session)
uow.categorias.create(categoria)  # uso el repositorio
uow.commit()  # confirmo la transacción
"""

from sqlmodel import Session
from .categoria_repository import CategoriaRepository
from .ingrediente_repository import IngredienteRepository
from .producto_repository import ProductoRepository
from .producto_ingrediente_repository import ProductoIngredienteRepository


class UnitOfWork:
    """
    UNIT OF WORK: Orquestador de repositorios y transacciones
    
    RESPONSABILIDADES:
    - Proporciona acceso a todos los repositorios
    - Gestiona la sesión y transacciones
    - Ejecuta commit/rollback
    """
    
    def __init__(self, session: Session):
        """
        CONSTRUCTOR
        
        PARÁMETRO:
        - session: conexión a la BD (inyectada por FastAPI)
        
        FLUJO:
        1. Almacena la sesión
        2. Crea 4 repositorios especializados (uno por modelo)
        3. Cada repositorio recibe la MISMA sesión
        
        ¿POR QUÉ MISMA SESIÓN?
        - Las operaciones deben estar en la misma transacción
        - session.commit() confirma TODAS las operaciones a la vez
        - Garantiza consistencia
        
        EJEMPLO:
        session = get_session()  # de la BD
        uow = UnitOfWork(session)
        # Ahora tenés acceso a:
        uow.categorias  # CategoriaRepository
        uow.ingredientes  # IngredienteRepository
        uow.productos  # ProductoRepository
        uow.producto_ingredientes  # ProductoIngredienteRepository
        """
        self.session = session
        
        # REPOSITORIO 1: Categorías
        self.categorias = CategoriaRepository(session)
        
        # REPOSITORIO 2: Ingredientes
        self.ingredientes = IngredienteRepository(session)
        
        # REPOSITORIO 3: Productos
        self.productos = ProductoRepository(session)
        
        # REPOSITORIO 4: Relación ProductoIngrediente (N:N)
        self.producto_ingredientes = ProductoIngredienteRepository(session)
    
    def commit(self):
        """
        CONFIRMAR TRANSACCIÓN
        
        FLUJO:
        1. session.commit() = confirma TODOS los cambios
        2. Escribe en la BD
        3. Si hay error → lanza exception
        
        ¿CUÁNDO USAR?
        - Al final de una operación exitosa
        - En el service (no en el repository)
        
        EJEMPLO:
        uow.categorias.create(categoria)
        uow.commit()  # Confirma el INSERT
        
        NOTA:
        - Si hay error antes de commit() → los cambios NO se guardan
        - Es por eso que validamos todo ANTES de persistir
        """
        self.session.commit()
    
    def rollback(self):
        """
        DESHACER CAMBIOS (Rollback)
        
        FLUJO:
        1. session.rollback() = descarta todos los cambios
        2. Vuelve al último commit()
        
        ¿CUÁNDO USAR?
        - Si ocurre un error y necesitamos revertir
        - En handlers de excepciones
        
        EJEMPLO:
        try:
            uow.categorias.create(categoria)
            uow.commit()
        except Exception as e:
            uow.rollback()  # Descarta el INSERT
            raise
        
        NOTA:
        - No es común usarlo en aplicaciones FastAPI
        - El server hace rollback automático en errores
        """
        self.session.rollback()
    
    def close(self):
        """
        CERRAR CONEXIÓN
        
        FLUJO:
        1. session.close() = libera la conexión
        
        ¿CUÁNDO USAR?
        - Al final de una request (FastAPI lo hace automático)
        - En testing después de cada test
        
        NOTA:
        - En FastAPI, el lifespan del contexto cierra automáticamente
        - No necesitas llamarlo manualmente en la mayoría de casos
        """
        self.session.close()