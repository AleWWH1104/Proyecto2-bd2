"""Router para Plataformas — Persona 1.

Endpoints:
    GET  /plataformas  - Listar todas las plataformas
    POST /plataformas  - Crear una nueva plataforma
"""

from fastapi import APIRouter
from typing import List
from app.models import PlataformaCreate, PlataformaResponse
from app import repositories

router = APIRouter(prefix="/plataformas", tags=["Plataformas"])


@router.get("", response_model=List[PlataformaResponse], summary="Listar plataformas")
def listar_plataformas():
    """Retorna todas las plataformas disponibles."""
    return repositories.plataformas.listar_plataformas()


@router.post("", response_model=PlataformaResponse, status_code=201, summary="Crear una plataforma")
def crear_plataforma(data: PlataformaCreate):
    """Crea un nuevo nodo Plataforma con sus propiedades."""
    return repositories.plataformas.crear_plataforma(data.model_dump())
