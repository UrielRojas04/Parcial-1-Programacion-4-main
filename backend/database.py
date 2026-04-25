"""
CONFIGURACIÓN: Base de Datos
=============================

PROPÓSITO:
- Conectar a PostgreSQL
- Crear tablas (si no existen)
- Proporcionar sesiones para FastAPI

FLUJO:
1. create_engine() = establece conexión
2. create_db() = crea tablas en lifespan
3. get_session() = generador que FastAPI inyecta en endpoints
"""

from sqlmodel import create_engine, SQLModel, Session
from dotenv import load_dotenv
import os
import models  # Importa TODOS los modelos para que se registren

# CARGAR VARIABLES DE ENTORNO
# .env debería tener: DATABASE_URL=postgresql://usuario:contraseña@localhost/nombre_bd
load_dotenv()

# OBTENER STRING DE CONEXIÓN
# Ejemplo: postgresql://postgres:password@localhost:5432/parcial
DATABASE_URL = os.getenv("DATABASE_URL")

# CREAR ENGINE (Motor de BD)
# engine = objeto que gestiona las conexiones a PostgreSQL
# echo=True = registra todas las queries SQL en la consola (útil para debug)
engine = create_engine(DATABASE_URL, echo=True)

def create_db():
    """
    CREAR TABLAS EN LA BD
    
    FLUJO:
    1. SQLModel.metadata = información de TODAS las tablas definidas
    2. create_all(engine) = CREATE TABLE ... IF NOT EXISTS para cada modelo
    3. Si la tabla ya existe → no hace nada
    
    ¿CUÁNDO SE LLAMA?
    - En main.py, en el lifespan (cuando inicia la aplicación)
    
    EJEMPLO:
    database.create_db()
    → Crea: tabla categoria, ingrediente, producto, producto_ingrediente
    
    TABLAS QUE CREA:
    - categoria
    - ingrediente
    - producto
    - producto_ingrediente
    """
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    GENERADOR DE SESIONES para FastAPI
    
    ¿QUÉ HACE?
    - Abre una conexión a la BD
    - yield = pausa, devuelve la sesión al endpoint
    - El endpoint usa la sesión
    - Al finalizar → with cierra la sesión automáticamente
    
    PATRÓN:
    - Es un generador (tiene yield)
    - FastAPI lo usa como dependencia
    - Abre y cierra sesión automáticamente
    
    ¿CUÁNDO SE LLAMA?
    - FastAPI: automáticamente en cada request
    - En routers: Depends(get_session)
    
    EJEMPLO FLUJO:
    1. GET /categorias/
    2. FastAPI ejecuta get_session()
    3. Abre Session(engine) → conexión
    4. Llama al endpoint con session inyectada
    5. Endpoint usa session
    6. Finaliza endpoint
    7. with cierra session automáticamente
    
    USO EN ROUTERS:
    SessionDep = Annotated[Session, Depends(get_session)]
    
    @router.get("/")
    def get_categorias(service: CategoriaServiceDep):
        # FastAPI automáticamente inyecta la sesión en el service
        pass
    """
    with Session(engine) as session:
        yield session