"""Router para Actores.

Endpoints:
    GET    /actores                              - Listar actores
    POST   /actores                              - Crear actor (con multi-label si es_director=true)
    PATCH  /actores/{aid}/agregar-director       - Multi-label dinámico (agrega :Director)
    POST   /actores/{aid}/actua-en/{sid}         - Vincular actor a serie con propiedades
    PATCH  /actores/{aid}/actua-en/{sid}         - Actualizar relación ACTUA_EN
    DELETE /actores/{aid}/actua-en/{sid}         - Desvincular actor de serie
"""
from fastapi import APIRouter, HTTPException

from app.models import (
    ActorCreate,
    ActorResponse,
    ActuaEnCreate,
    ActuaEnPatch,
)
from app.repositories import actores as actores_repo


router = APIRouter(prefix="/actores", tags=["Actores"])


@router.get("", summary="Listar actores")
def listar_actores():
    return {"actores": actores_repo.listar()}


@router.post(
    "",
    response_model=ActorResponse,
    status_code=201,
    summary="Crear actor (multi-label si es_director=true)",
)
def crear_actor(datos: ActorCreate):
    """Crea un nodo Actor. Si `es_director` es true → multi-label `:Actor:Director`.

    Rúbrica: Crear nodo 2+ labels (multi-label).
    """
    return actores_repo.crear(datos.model_dump())


@router.patch(
    "/{actor_id}/agregar-director",
    response_model=ActorResponse,
    summary="Agregar label :Director a un actor existente",
)
def agregar_director(actor_id: str):
    """Agrega el label `:Director` a un Actor ya creado (multi-label dinámico).

    Rúbrica: Multi-label dinámico.
    """
    actor = actores_repo.agregar_label_director(actor_id)
    if actor is None:
        raise HTTPException(status_code=404, detail=f"Actor {actor_id} no encontrado")
    return actor


@router.post(
    "/{actor_id}/actua-en/{serie_id}",
    status_code=201,
    summary="Vincular actor a serie (relación ACTUA_EN)",
)
def crear_actua_en(actor_id: str, serie_id: str, datos: ActuaEnCreate):
    """Crea la relación ACTUA_EN entre Actor y Serie con propiedades.

    Rúbrica: Crear relación con propiedades.
    """
    rel = actores_repo.crear_actua_en(actor_id, serie_id, datos.model_dump())
    if rel is None:
        raise HTTPException(
            status_code=404,
            detail=f"Actor {actor_id} o Serie {serie_id} no encontrado",
        )
    return {"mensaje": "Relación ACTUA_EN creada", "relacion": rel}


@router.patch(
    "/{actor_id}/actua-en/{serie_id}",
    summary="Actualizar relación ACTUA_EN",
)
def actualizar_actua_en(actor_id: str, serie_id: str, datos: ActuaEnPatch):
    """Actualiza propiedades de la relación ACTUA_EN existente.

    Rúbrica: Gestión props relaciones — 1 relación.
    """
    rel = actores_repo.actualizar_actua_en(actor_id, serie_id, datos.model_dump())
    if rel is None:
        raise HTTPException(
            status_code=404,
            detail=f"Relación ACTUA_EN entre {actor_id} y {serie_id} no encontrada",
        )
    return {"mensaje": "Relación ACTUA_EN actualizada", "relacion": rel}


@router.delete(
    "/{actor_id}/actua-en/{serie_id}",
    summary="Desvincular actor de serie",
)
def eliminar_actua_en(actor_id: str, serie_id: str):
    """Elimina la relación ACTUA_EN entre el actor y la serie.

    Rúbrica: Eliminar 1 relación.
    """
    ok = actores_repo.eliminar_actua_en(actor_id, serie_id)
    if not ok:
        raise HTTPException(
            status_code=404,
            detail=f"Relación ACTUA_EN entre {actor_id} y {serie_id} no encontrada",
        )
    return {"mensaje": f"Relación ACTUA_EN entre {actor_id} y {serie_id} eliminada"}
