"""Router para reseñas.

Endpoints HTTP para el nodo Resena. Crear una reseña arma en una sola
operación: el nodo Resena + ESCRIBIO (Usuario→Resena) + SOBRE (Resena→Serie).
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models import (
    ResenaCreate,
    ResenaPatch,
    ResenaResponse,
    ResenasListResponse,
)
from app.repositories import resenas as resenas_repo


router = APIRouter(prefix="/resenas", tags=["Reseñas"])


@router.get("", response_model=ResenasListResponse, summary="Listar reseñas con filtros")
def listar_resenas(
    usuario_id: Optional[str] = Query(None, description="Filtrar por autor"),
    serie_id: Optional[str] = Query(None, description="Filtrar por serie"),
    puntuacion_min: Optional[int] = Query(None, ge=1, le=10),
    puntuacion_max: Optional[int] = Query(None, ge=1, le=10),
    contiene_spoilers: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """Lista reseñas con filtros opcionales y paginación."""
    return resenas_repo.listar(
        usuario_id=usuario_id,
        serie_id=serie_id,
        puntuacion_min=puntuacion_min,
        puntuacion_max=puntuacion_max,
        contiene_spoilers=contiene_spoilers,
        skip=skip,
        limit=limit,
    )


@router.post("", response_model=ResenaResponse, status_code=201, summary="Crear reseña")
def crear_resena(datos: ResenaCreate):
    """Crea Resena + ESCRIBIO + SOBRE en una sola operación.

    El backend genera `id`, `fecha` (hoy) y arranca `util` en 0.
    """
    resena = resenas_repo.crear(
        usuario_id=datos.usuario_id,
        serie_id=datos.serie_id,
        titulo=datos.titulo,
        texto=datos.texto,
        puntuacion=datos.puntuacion,
        etiquetas=datos.etiquetas,
        visibilidad=datos.visibilidad,
        contieneSpoilers=datos.contieneSpoilers,
        temporadaAfectada=datos.temporadaAfectada,
        protagonista=datos.protagonista,
    )
    if resena is None:
        raise HTTPException(
            status_code=404,
            detail=f"Usuario {datos.usuario_id} o Serie {datos.serie_id} no encontrado",
        )
    return resena


@router.patch(
    "/{resena_id}", response_model=ResenaResponse, summary="Editar reseña propia"
)
def actualizar_resena(resena_id: str, datos: ResenaPatch):
    """Actualiza propiedades del nodo Resena y marca ESCRIBIO.editada = true.

    No permite cambiar `id` ni `fecha`.
    Rúbrica: Gestión de propiedades de nodos — 1 nodo.
    """
    resena = resenas_repo.actualizar(resena_id, datos.propiedades)
    if resena is None:
        raise HTTPException(status_code=404, detail=f"Reseña {resena_id} no encontrada")
    return resena


@router.delete("/{resena_id}", status_code=204, summary="Eliminar reseña")
def eliminar_resena(resena_id: str):
    """Elimina la reseña con DETACH DELETE — borra ESCRIBIO y SOBRE también."""
    eliminado = resenas_repo.eliminar(resena_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail=f"Reseña {resena_id} no encontrada")
    # 204 No Content
