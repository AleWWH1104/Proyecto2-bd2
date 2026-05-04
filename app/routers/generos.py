"""Router para Generos — Persona 1.

Endpoints:
    GET  /generos  - Listar todos los géneros
    POST /generos  - Crear un nuevo género
"""

from fastapi import APIRouter
from typing import List
from app.models import GeneroCreate, GeneroResponse
from app import repositories

router = APIRouter(prefix="/generos", tags=["Generos"])


@router.get("", response_model=List[GeneroResponse], summary="Listar géneros")
def listar_generos():
    """Retorna todos los géneros disponibles (para poblar selectores)."""
    return repositories.generos.listar_generos()


@router.post("", response_model=GeneroResponse, status_code=201, summary="Crear un género")
def crear_genero(data: GeneroCreate):
    """Crea un nuevo nodo Genero con sus propiedades."""
    return repositories.generos.crear_genero(data.model_dump())
