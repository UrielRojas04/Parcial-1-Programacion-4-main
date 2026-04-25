"""
PUNTO DE ENTRADA: FastAPI Application
======================================

PROPÓSITO:
- Inicializa la aplicación FastAPI
- Configura middleware (CORS)
- Ejecuta hooks de startup (crear tablas)
- Registra routers (endpoints)

FLUJO DE INICIO:
1. @asynccontextmanager lifespan() se ejecuta
2. Crea las tablas en la BD (create_db)
3. yield = la app está lista para recibir requests
4. Requests se procesan (routers)
5. Al finalizar: código después de yield
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_db
from routers import categorias, ingredientes, productos

# ========== LIFESPAN (Hooks de Startup/Shutdown) ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    LIFESPAN: gestiona la vida de la aplicación
    
    ANTES DE yield = STARTUP (cuando inicia)
    DESPUÉS DE yield = SHUTDOWN (cuando finaliza)
    
    ¿QUÉ HACEMOS?
    1. create_db() = crea las tablas en PostgreSQL
    2. yield = la app está lista
    3. (nada después = no hay tareas de shutdown)
    
    FLUJO:
    1. FastAPI inicia
    2. Ejecuta lifespan()
    3. Llama create_db() → CREATE TABLE ... IF NOT EXISTS
    4. yield = pausa, la app recibe requests
    5. Usuario hace requests (GET /categorias/, POST /productos/, etc.)
    6. Finaliza la app → código después de yield
    
    ¿POR QUÉ async def?
    - FastAPI es asincrónico
    - lifespan puede hacer await si necesita I/O async
    """
    # STARTUP: se ejecuta al iniciar la app
    create_db()  # Crea tablas si no existen
    # Aquí podrías: conectar a Redis, inicializar caché, etc.
    
    # yield = pausa, la app comienza a procesar requests
    yield
    
    # SHUTDOWN: se ejecuta al apagar la app
    # Aquí podrías: cerrar conexiones a servicios, limpiar recursos, etc.


# ========== CREAR APLICACIÓN ==========
app = FastAPI(lifespan=lifespan)

# ========== MIDDLEWARE: CORS ==========
# CORS = Cross-Origin Resource Sharing
# Permite que el FRONTEND (en localhost:5173) hable con el BACKEND (en localhost:8000)
#
# SIN CORS:
# - Frontend hace fetch a http://localhost:8000/categorias/
# - Navegador bloquea → "No 'Access-Control-Allow-Origin' header"
#
# CON CORS:
# - Backend autoriza al frontend
# - Solicitudes cruzadas se permiten
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend Vite en dev
    allow_methods=["*"],  # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Permite cualquier header
)

# ========== REGISTRAR ROUTERS ==========
# Los routers contienen los endpoints
# include_router() los agrega a la app

# Router de Categorías: /categorias/
app.include_router(categorias.router)

# Router de Ingredientes: /ingredientes/
app.include_router(ingredientes.router)

# Router de Productos: /productos/
app.include_router(productos.router)

# ========== HEALTH CHECK ==========
@app.get("/")
def root():
    """
    ENDPOINT DE PRUEBA
    
    Propósito: verificar que la API funciona
    
    EJEMPLO:
    curl http://localhost:8000/
    → {"message": "Api funcionando correctamente"}
    
    CUÁNDO LLAMARLO:
    - Para verificar que el servidor está vivo
    - Para testear CORS (frontend lo puede llamar)
    """
    return {"message": "Api funcionando correctamente"}


# ========== ESTRUCTURA RESUMIDA ==========
# /                    → root() health check
# /categorias/         → GET lista, POST crear, PUT editar, DELETE eliminar
# /ingredientes/       → GET lista, POST crear, PUT editar, DELETE eliminar
# /productos/          → GET lista, POST crear, PUT editar, DELETE eliminar
# /productos/{id}/ingredientes/  → GET ingredientes, POST agregar, DELETE quitar

# ========== PARA EJECUTAR ==========
# Terminal: cd backend
# Terminal: python -m uvicorn main:app --reload
# Abre: http://localhost:8000/docs (Swagger UI)