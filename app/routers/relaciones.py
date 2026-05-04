"""Router para Relaciones — Persona 1.

Endpoints:
    POST   /relaciones/pertenece-a/{serie_id}/{genero_id}    - Crear PERTENECE_A
    PATCH  /relaciones/pertenece-a/{serie_id}/{genero_id}    - Actualizar PERTENECE_A
    DELETE /relaciones/pertenece-a/{serie_id}/{genero_id}    - Eliminar PERTENECE_A
    POST   /relaciones/transmite/{plataforma_id}/{serie_id}  - Crear TRANSMITE
    POST   /relaciones/similar-a/{serie1_id}/{serie2_id}     - Crear SIMILAR_A
"""

from fastapi import APIRouter, HTTPException
from app.models import (
    PerteneceACreate,
    PerteneceAPatch,
    TransmiteCreate,
    SimilarACreate,
)
from app import repositories

router = APIRouter(prefix="/relaciones", tags=["Relaciones"])


# ============================================
# PERTENECE_A
# ============================================


@router.post(
    "/pertenece-a/{serie_id}/{genero_id}",
    status_code=201,
    summary="Crear relación PERTENECE_A (Serie → Genero)",
)
def crear_pertenece_a(serie_id: str, genero_id: str, body: PerteneceACreate):
    """Crea la relación PERTENECE_A con 3 propiedades.

    Valida que Serie y Genero existan antes de crear la relación.
    """
    data = body.model_dump()
    relacion = repositories.relaciones.crear_pertenece_a(serie_id, genero_id, data)
    if not relacion:
        raise HTTPException(
            status_code=404,
            detail=f"Serie '{serie_id}' o Genero '{genero_id}' no encontrados",
        )
    return relacion


@router.patch(
    "/pertenece-a/{serie_id}/{genero_id}",
    summary="Actualizar propiedades de relación PERTENECE_A",
)
def actualizar_pertenece_a(serie_id: str, genero_id: str, body: PerteneceAPatch):
    """Actualiza una o más propiedades de la relación PERTENECE_A."""
    relacion = repositories.relaciones.actualizar_pertenece_a(serie_id, genero_id, body.propiedades)
    if not relacion:
        raise HTTPException(
            status_code=404,
            detail=f"Relación PERTENECE_A entre '{serie_id}' y '{genero_id}' no encontrada",
        )
    return relacion


@router.delete(
    "/pertenece-a/{serie_id}/{genero_id}",
    summary="Eliminar relación PERTENECE_A",
)
def eliminar_pertenece_a(serie_id: str, genero_id: str):
    """Elimina la relación PERTENECE_A entre una Serie y un Genero."""
    ok = repositories.relaciones.eliminar_pertenece_a(serie_id, genero_id)
    if not ok:
        raise HTTPException(
            status_code=404,
            detail=f"Relación PERTENECE_A entre '{serie_id}' y '{genero_id}' no encontrada",
        )
    return {"mensaje": f"Relación PERTENECE_A entre '{serie_id}' y '{genero_id}' eliminada"}


# ============================================
# TRANSMITE
# ============================================


@router.post(
    "/transmite/{plataforma_id}/{serie_id}",
    status_code=201,
    summary="Crear relación TRANSMITE (Plataforma → Serie)",
)
def crear_transmite(plataforma_id: str, serie_id: str, body: TransmiteCreate):
    """Crea la relación TRANSMITE con 3 propiedades.

    Valida que Plataforma y Serie existan antes de crear la relación.
    """
    data = body.model_dump()
    relacion = repositories.relaciones.crear_transmite(plataforma_id, serie_id, data)
    if not relacion:
        raise HTTPException(
            status_code=404,
            detail=f"Plataforma '{plataforma_id}' o Serie '{serie_id}' no encontrados",
        )
    return relacion


# ============================================
# SIMILAR_A
# ============================================


@router.post(
    "/similar-a/{serie1_id}/{serie2_id}",
    status_code=201,
    summary="Crear relación SIMILAR_A (Serie → Serie)",
)
def crear_similar_a(serie1_id: str, serie2_id: str, body: SimilarACreate):
    """Crea la relación SIMILAR_A entre dos Series con 3 propiedades.

    Valida que ambas Series existan antes de crear la relación.
    """
    data = body.model_dump()
    relacion = repositories.relaciones.crear_similar_a(serie1_id, serie2_id, data)
    if not relacion:
        raise HTTPException(
            status_code=404,
            detail=f"Serie '{serie1_id}' o Serie '{serie2_id}' no encontradas",
        )
    return relacion
