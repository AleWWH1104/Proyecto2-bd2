from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Neo4jDriver
from app.routers import (
    actores,
    admin,
    consultas,
    relaciones,
    resenas,
    series,
    usuarios,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando aplicación...")
    if Neo4jDriver.verify_connectivity():
        print("Conectado a Neo4j correctamente")
    else:
        print("ADVERTENCIA: no se pudo conectar a Neo4j. Verifica tu .env")
    yield
    Neo4jDriver.close()
    print("Conexión a Neo4j cerrada")

app = FastAPI(
    title="Motor de Recomendación de Series",
    description=(
        "Proyecto 2 - Neo4j - CC3089 Base de Datos 2\n\n"
        "API REST que implementa un motor de recomendación de series usando "
        "una base de datos orientada a grafos (Neo4j)."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ============================================
# CORS
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# ENDPOINTS BASE
# ============================================
@app.get("/", tags=["Base"])
def root():
    return {
        "mensaje": "API funcionando correctamente",
        "documentacion_swagger": "/docs",
        "documentacion_redoc": "/redoc",
        "health_check": "/health",
    }

@app.get("/health", tags=["Base"])
def health():
    connected = Neo4jDriver.verify_connectivity()
    return {
        "status": "ok" if connected else "degraded",
        "neo4j": "conectado" if connected else "sin conexión",
    }

# ============================================
# REGISTRO DE ROUTERS
# ============================================
app.include_router(series.router)
app.include_router(usuarios.router)
app.include_router(relaciones.router)
app.include_router(resenas.router)
app.include_router(actores.router)
app.include_router(consultas.router)
app.include_router(admin.router)