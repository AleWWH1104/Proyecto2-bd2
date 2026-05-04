"""Entry point de la aplicación FastAPI.

Inicializa la app, conecta a Neo4j y registra todos los routers.
Para correr: uv run uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import Neo4jDriver

# Importar routers (se irán agregando conforme se creen)
from app.routers import usuarios, relaciones, resenas
# from app.routers import (
#     series,
#     actores,
#     generos,
#     plataformas,
#     estudios,
#     consultas,
#     admin,
# )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Maneja el ciclo de vida de la app: conexión al iniciar, cierre al apagar."""
    # Startup
    print("Iniciando aplicación...")
    if Neo4jDriver.verify_connectivity():
        print("Conectado a Neo4j correctamente")
    else:
        print("ADVERTENCIA: no se pudo conectar a Neo4j. Verifica tu .env")

    yield

    # Shutdown
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
# REGISTRO DE ROUTERS
# ============================================
# Descomenta cada uno conforme se vayan creando

app.include_router(usuarios.router)
app.include_router(relaciones.router)
app.include_router(resenas.router)
# app.include_router(series.router)
# app.include_router(actores.router)
# app.include_router(generos.router)
# app.include_router(plataformas.router)
# app.include_router(estudios.router)
# app.include_router(consultas.router)
# app.include_router(admin.router)
