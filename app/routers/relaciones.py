"""Router para relaciones de Persona 1 y Persona 2."""

from fastapi import APIRouter, HTTPException

from app.models import (
    EnListaCreate,
    LeGustaCreate,
    LeGustaEliminarMasivo,
    OperacionMasivaResponse,
    PerteneceACreate,
    PerteneceAPatch,
    RelacionResponse,
    SigueACreate,
    SimilarACreate,
    TransmiteCreate,
    VioCreate,
    VioPatch,
    VioMasivoUpdate,
)
from app.repositories import relaciones as relaciones_repo


router = APIRouter()


# ============================================
# PERSONA 1 — RELACIONES DE SERIE
# ============================================


@router.post(
    "/relaciones/pertenece-a/{serie_id}/{genero_id}",
    status_code=201,
    tags=["Relaciones"],
    summary="Crear relación PERTENECE_A (Serie → Genero)",
)
def crear_pertenece_a(serie_id: str, genero_id: str, body: PerteneceACreate):
    relacion = relaciones_repo.crear_pertenece_a(serie_id, genero_id, body.model_dump())
    if not relacion:
        raise HTTPException(
            status_code=404,
            detail=f"Serie '{serie_id}' o Genero '{genero_id}' no encontrados",
        )
    return relacion


@router.patch(
    "/relaciones/pertenece-a/{serie_id}/{genero_id}",
    tags=["Relaciones"],
    summary="Actualizar propiedades de PERTENECE_A",
)
def actualizar_pertenece_a(serie_id: str, genero_id: str, body: PerteneceAPatch):
    relacion = relaciones_repo.actualizar_pertenece_a(serie_id, genero_id, body.propiedades)
    if not relacion:
        raise HTTPException(
            status_code=404,
            detail=f"Relación PERTENECE_A entre '{serie_id}' y '{genero_id}' no encontrada",
        )
    return relacion


@router.delete(
    "/relaciones/pertenece-a/{serie_id}/{genero_id}",
    tags=["Relaciones"],
    summary="Eliminar relación PERTENECE_A",
)
def eliminar_pertenece_a(serie_id: str, genero_id: str):
    ok = relaciones_repo.eliminar_pertenece_a(serie_id, genero_id)
    if not ok:
        raise HTTPException(
            status_code=404,
            detail=f"Relación PERTENECE_A entre '{serie_id}' y '{genero_id}' no encontrada",
        )
    return {"mensaje": f"Relación PERTENECE_A entre '{serie_id}' y '{genero_id}' eliminada"}


@router.post(
    "/relaciones/transmite/{plataforma_id}/{serie_id}",
    status_code=201,
    tags=["Relaciones"],
    summary="Crear relación TRANSMITE (Plataforma → Serie)",
)
def crear_transmite(plataforma_id: str, serie_id: str, body: TransmiteCreate):
    relacion = relaciones_repo.crear_transmite(plataforma_id, serie_id, body.model_dump())
    if not relacion:
        raise HTTPException(
            status_code=404,
            detail=f"Plataforma '{plataforma_id}' o Serie '{serie_id}' no encontrados",
        )
    return relacion


@router.post(
    "/relaciones/similar-a/{serie1_id}/{serie2_id}",
    status_code=201,
    tags=["Relaciones"],
    summary="Crear relación SIMILAR_A (Serie → Serie)",
)
def crear_similar_a(serie1_id: str, serie2_id: str, body: SimilarACreate):
    relacion = relaciones_repo.crear_similar_a(serie1_id, serie2_id, body.model_dump())
    if not relacion:
        raise HTTPException(
            status_code=404,
            detail=f"Serie '{serie1_id}' o Serie '{serie2_id}' no encontradas",
        )
    return relacion


# ============================================
# PERSONA 2 — RELACIONES DE USUARIO
# ============================================


@router.post(
    "/usuarios/{usuario_id}/vio/{serie_id}",
    response_model=RelacionResponse,
    status_code=201,
    tags=["Relaciones Usuario→Serie"],
    summary="Marcar serie como vista",
)
def marcar_vio(usuario_id: str, serie_id: str, datos: VioCreate):
    """Crea la relación VIO con propiedades.

    Rúbrica: Crear relación con propiedades.
    """
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


# IMPORTANTE: /vio/masivo debe declararse ANTES de /vio/{serie_id}
# para que FastAPI no interprete "masivo" como un serie_id.
@router.patch(
    "/usuarios/{usuario_id}/vio/masivo",
    response_model=OperacionMasivaResponse,
    tags=["Relaciones Usuario→Serie"],
    summary="Actualizar progreso de varias series",
)
def actualizar_vio_masivo(usuario_id: str, datos: VioMasivoUpdate):
    """Actualiza el progreso de varias relaciones VIO en una sola operación.

    Rúbrica: Gestión props relaciones — masivo.
    """
    items = [item.model_dump() for item in datos.items]
    afectados = relaciones_repo.actualizar_vio_masivo(usuario_id, items)
    return {"mensaje": "Actualización masiva de VIO completada", "afectados": afectados}


@router.patch(
    "/usuarios/{usuario_id}/vio/{serie_id}",
    response_model=RelacionResponse,
    tags=["Relaciones Usuario→Serie"],
    summary="Actualizar progreso (% visto, completada)",
)
def actualizar_vio(usuario_id: str, serie_id: str, datos: VioPatch):
    """Actualiza propiedades de la relación VIO existente.

    Rúbrica: Gestión props relaciones — 1 relación.
    """
    rel = relaciones_repo.actualizar_vio(
        usuario_id=usuario_id,
        serie_id=serie_id,
        porcentajeVisto=datos.porcentajeVisto,
        completada=datos.completada,
        calificacion=datos.calificacion,
    )
    if rel is None:
        raise HTTPException(
            status_code=404,
            detail=f"Relación VIO entre usuario {usuario_id} y serie {serie_id} no encontrada",
        )
    return {"mensaje": "Relación VIO actualizada", "relacion": rel}


@router.delete(
    "/usuarios/{usuario_id}/vio/{serie_id}",
    tags=["Relaciones Usuario→Serie"],
    summary="Quitar serie del historial",
)
def eliminar_vio(usuario_id: str, serie_id: str):
    """Elimina la relación VIO entre el usuario y la serie.

    Rúbrica: Eliminar 1 relación.
    """
    ok = relaciones_repo.eliminar_vio(usuario_id, serie_id)
    if not ok:
        raise HTTPException(
            status_code=404,
            detail=f"Relación VIO entre usuario {usuario_id} y serie {serie_id} no encontrada",
        )
    return {"mensaje": f"Relación VIO entre {usuario_id} y {serie_id} eliminada"}


@router.post(
    "/usuarios/{usuario_id}/le-gusta/{serie_id}",
    response_model=RelacionResponse,
    status_code=201,
    tags=["Relaciones Usuario→Serie"],
    summary="Dar like a una serie",
)
def dar_like(usuario_id: str, serie_id: str, datos: LeGustaCreate):
    """Crea la relación LE_GUSTA con propiedades.

    Rúbrica: Crear relación con propiedades.
    """
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


# IMPORTANTE: /le-gusta/masivo debe ir ANTES de /le-gusta/{serie_id}
# para que FastAPI no interprete "masivo" como serie_id.
@router.delete(
    "/usuarios/{usuario_id}/le-gusta/masivo",
    response_model=OperacionMasivaResponse,
    tags=["Relaciones Usuario→Serie"],
    summary="Quitar like a varias series",
)
def quitar_like_masivo(usuario_id: str, datos: LeGustaEliminarMasivo):
    """Elimina varias relaciones LE_GUSTA en una sola operación.

    Rúbrica: Eliminar múltiples relaciones.
    """
    afectados = relaciones_repo.quitar_like_masivo(usuario_id, datos.serie_ids)
    return {"mensaje": "Likes eliminados", "afectados": afectados}


@router.delete(
    "/usuarios/{usuario_id}/le-gusta/{serie_id}",
    tags=["Relaciones Usuario→Serie"],
    summary="Quitar like a una serie",
)
def quitar_like(usuario_id: str, serie_id: str):
    """Elimina la relación LE_GUSTA entre el usuario y la serie.

    Rúbrica: Eliminar 1 relación.
    """
    ok = relaciones_repo.quitar_like(usuario_id, serie_id)
    if not ok:
        raise HTTPException(
            status_code=404,
            detail=f"Relación LE_GUSTA entre usuario {usuario_id} y serie {serie_id} no encontrada",
        )
    return {"mensaje": f"Like de {usuario_id} a {serie_id} eliminado"}


@router.post(
    "/usuarios/{usuario_id}/en-lista/{serie_id}",
    response_model=RelacionResponse,
    status_code=201,
    tags=["Relaciones Usuario→Serie"],
    summary="Agregar serie a la watchlist",
)
def agregar_a_lista(usuario_id: str, serie_id: str, datos: EnListaCreate):
    """Crea la relación EN_LISTA con propiedades.

    Rúbrica: Crear relación con propiedades.
    """
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


@router.delete(
    "/usuarios/{usuario_id}/en-lista/{serie_id}",
    tags=["Relaciones Usuario→Serie"],
    summary="Quitar serie de la watchlist",
)
def quitar_de_lista(usuario_id: str, serie_id: str):
    """Elimina la relación EN_LISTA entre el usuario y la serie.

    Rúbrica: Eliminar 1 relación.
    """
    ok = relaciones_repo.quitar_de_lista(usuario_id, serie_id)
    if not ok:
        raise HTTPException(
            status_code=404,
            detail=f"Relación EN_LISTA entre usuario {usuario_id} y serie {serie_id} no encontrada",
        )
    return {"mensaje": f"Serie {serie_id} quitada de la watchlist de {usuario_id}"}


@router.post(
    "/usuarios/{usuario_id}/sigue/{otro_usuario_id}",
    response_model=RelacionResponse,
    status_code=201,
    tags=["Relaciones Usuario→Usuario"],
    summary="Seguir a otro usuario",
)
def seguir(usuario_id: str, otro_usuario_id: str, datos: SigueACreate):
    """Crea la relación SIGUE_A con propiedades. Mantiene el flag `mutuo`.

    Rúbrica: Crear relación con propiedades.
    """
    if usuario_id == otro_usuario_id:
        raise HTTPException(status_code=400, detail="Un usuario no puede seguirse a sí mismo")

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


@router.delete(
    "/usuarios/{usuario_id}/sigue/{otro_usuario_id}",
    tags=["Relaciones Usuario→Usuario"],
    summary="Dejar de seguir a un usuario",
)
def dejar_de_seguir(usuario_id: str, otro_usuario_id: str):
    """Elimina la relación SIGUE_A. Si la inversa existe, marca su `mutuo` como false.

    Rúbrica: Eliminar 1 relación.
    """
    ok = relaciones_repo.dejar_de_seguir(usuario_id, otro_usuario_id)
    if not ok:
        raise HTTPException(
            status_code=404,
            detail=f"Relación SIGUE_A entre {usuario_id} y {otro_usuario_id} no encontrada",
        )
    return {"mensaje": f"{usuario_id} dejó de seguir a {otro_usuario_id}"}
