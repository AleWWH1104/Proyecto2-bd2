"""Router para relaciones del Usuario.

Agrupa los endpoints HTTP de las relaciones que parten del nodo Usuario:
- Usuario→Serie:   VIO, LE_GUSTA, EN_LISTA
- Usuario→Usuario: SIGUE_A

Todos los paths cuelgan de /usuarios/{usuario_id}/... — usan el mismo
prefijo que el router de usuarios pero los endpoints son distintos, así
que FastAPI los enruta sin conflicto.
"""
from fastapi import APIRouter, HTTPException

from app.models import (
    VioCreate,
    VioMasivoUpdate,
    LeGustaCreate,
    LeGustaEliminarMasivo,
    EnListaCreate,
    SigueACreate,
    RelacionResponse,
    OperacionMasivaResponse,
)
from app.repositories import relaciones as relaciones_repo


router = APIRouter(prefix="/usuarios")


# ============================================
# Relaciones Usuario→Serie
# ============================================

@router.post(
    "/{usuario_id}/vio/{serie_id}",
    response_model=RelacionResponse,
    tags=["Relaciones Usuario→Serie"],
    summary="Marcar serie como vista (MERGE: crea o actualiza)",
)
def marcar_vio(usuario_id: str, serie_id: str, datos: VioCreate):
    """Crea o actualiza la relación VIO entre usuario y serie."""
    rel = relaciones_repo.marcar_vio(
        usuario_id=usuario_id,
        serie_id=serie_id,
        porcentajeVisto=datos.porcentajeVisto,
        completada=datos.completada,
        calificacion=datos.calificacion,
    )
    if rel is None:
        raise HTTPException(
            status_code=404,
            detail=f"Usuario {usuario_id} o Serie {serie_id} no encontrado",
        )
    return {"mensaje": "Relación VIO creada/actualizada", "relacion": rel}


@router.patch(
    "/{usuario_id}/vio-masivo",
    response_model=OperacionMasivaResponse,
    tags=["Relaciones Usuario→Serie"],
    summary="Actualizar varias VIO del usuario",
)
def actualizar_vio_masivo(usuario_id: str, datos: VioMasivoUpdate):
    """Actualiza propiedades de varias relaciones VIO en una sola operación."""
    items = [item.model_dump() for item in datos.items]
    afectados = relaciones_repo.actualizar_vio_masivo(usuario_id, items)
    return {"mensaje": "Actualización masiva de VIO completada", "afectados": afectados}


@router.post(
    "/{usuario_id}/le-gusta/{serie_id}",
    response_model=RelacionResponse,
    tags=["Relaciones Usuario→Serie"],
    summary="Dar like a una serie",
)
def dar_like(usuario_id: str, serie_id: str, datos: LeGustaCreate):
    """Crea o actualiza la relación LE_GUSTA."""
    rel = relaciones_repo.dar_like(
        usuario_id=usuario_id,
        serie_id=serie_id,
        puntuacion=datos.puntuacion,
        notificarx=datos.notificarx,
    )
    if rel is None:
        raise HTTPException(
            status_code=404,
            detail=f"Usuario {usuario_id} o Serie {serie_id} no encontrado",
        )
    return {"mensaje": "Relación LE_GUSTA creada/actualizada", "relacion": rel}


@router.delete(
    "/{usuario_id}/le-gusta-masivo",
    response_model=OperacionMasivaResponse,
    tags=["Relaciones Usuario→Serie"],
    summary="Quitar like a varias series",
)
def quitar_like_masivo(usuario_id: str, datos: LeGustaEliminarMasivo):
    """Elimina varias relaciones LE_GUSTA del usuario en una sola operación."""
    afectados = relaciones_repo.quitar_like_masivo(usuario_id, datos.serie_ids)
    return {"mensaje": "Likes eliminados", "afectados": afectados}


@router.post(
    "/{usuario_id}/en-lista/{serie_id}",
    response_model=RelacionResponse,
    tags=["Relaciones Usuario→Serie"],
    summary="Agregar serie a la lista del usuario",
)
def agregar_a_lista(usuario_id: str, serie_id: str, datos: EnListaCreate):
    """Crea o actualiza la relación EN_LISTA."""
    rel = relaciones_repo.agregar_a_lista(
        usuario_id=usuario_id,
        serie_id=serie_id,
        prioridad=datos.prioridad,
        notificaciones=datos.notificaciones,
    )
    if rel is None:
        raise HTTPException(
            status_code=404,
            detail=f"Usuario {usuario_id} o Serie {serie_id} no encontrado",
        )
    return {"mensaje": "Relación EN_LISTA creada/actualizada", "relacion": rel}


# ============================================
# Relaciones Usuario→Usuario
# ============================================

@router.post(
    "/{usuario_id}/sigue/{otro_usuario_id}",
    response_model=RelacionResponse,
    tags=["Relaciones Usuario→Usuario"],
    summary="Seguir a otro usuario",
)
def seguir(usuario_id: str, otro_usuario_id: str, datos: SigueACreate):
    """Crea o actualiza SIGUE_A. Marca `mutuo=true` si el otro ya sigue de vuelta."""
    if usuario_id == otro_usuario_id:
        raise HTTPException(
            status_code=400, detail="Un usuario no puede seguirse a sí mismo"
        )
    rel = relaciones_repo.seguir(
        usuario_id=usuario_id,
        otro_usuario_id=otro_usuario_id,
        notificaciones=datos.notificaciones,
    )
    if rel is None:
        raise HTTPException(
            status_code=404,
            detail=f"Usuario {usuario_id} o {otro_usuario_id} no encontrado",
        )
    return {"mensaje": "Relación SIGUE_A creada/actualizada", "relacion": rel}
