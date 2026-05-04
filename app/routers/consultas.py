"""Router para consultas analíticas y motor de recomendación.

Endpoints que no son CRUD de una entidad: cruzan varios nodos y relaciones
para responder preguntas de negocio.

Como los paths viven en distintos prefijos (/usuarios/.../recomendaciones
y /consultas/...), el router se declara sin prefix y cada endpoint usa
su path completo.
"""
from fastapi import APIRouter, HTTPException, Query

from app.models import (
    RecomendacionesResponse,
    UsuariosInfluyentesResponse,
)
from app.repositories import consultas as consultas_repo


router = APIRouter()


@router.get(
    "/usuarios/{usuario_id}/recomendaciones",
    response_model=RecomendacionesResponse,
    tags=["Consultas"],
    summary="Motor de recomendación (caso de uso central)",
)
def recomendaciones(
    usuario_id: str,
    limit: int = Query(10, ge=1, le=50, description="Máximo de series a sugerir"),
):
    """Filtrado colaborativo: series que les gustan a usuarios con gustos similares.

    Excluye lo que el usuario ya VIO, le gustan o tiene EN_LISTA.
    Devuelve 404 si el usuario no existe; lista vacía si existe pero aún
    no tiene suficientes datos para recomendar.
    """
    if not consultas_repo.usuario_existe(usuario_id):
        raise HTTPException(status_code=404, detail=f"Usuario {usuario_id} no encontrado")

    items = consultas_repo.recomendaciones_para_usuario(usuario_id, limit=limit)
    return {"usuario_id": usuario_id, "total": len(items), "items": items}


@router.get(
    "/consultas/usuarios-influyentes",
    response_model=UsuariosInfluyentesResponse,
    tags=["Consultas"],
    summary="Top usuarios con más seguidores y reseñas",
)
def usuarios_influyentes(
    limit: int = Query(10, ge=1, le=50, description="Cantidad de usuarios en el top"),
):
    """Ranking de usuarios por influencia = `seguidores * 2 + reseñas`."""
    items = consultas_repo.usuarios_influyentes(limit=limit)
    return {"total": len(items), "items": items}
