from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database import create_db
from routers import categorias, ingredientes, productos
from exceptions import DuplicateNameError, ErrorCode


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Manejador de excepciones para errores de nombres duplicados
@app.exception_handler(DuplicateNameError)
async def duplicate_name_exception_handler(request: Request, exc: DuplicateNameError):
    """Convierte excepciones de nombres duplicados a HTTP 409 Conflict"""
    return JSONResponse(
        status_code=409,
        content={
            "detail": exc.message,
            "error_code": exc.error_code.value,
            "nombre": exc.nombre,
        },
    )


app.include_router(categorias.router)
app.include_router(ingredientes.router)
app.include_router(productos.router)


@app.get("/")
def root():
    return {"message": "Api funcionando correctamente"}
