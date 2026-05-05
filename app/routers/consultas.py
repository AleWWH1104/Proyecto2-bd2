"""Router para consultas analíticas y motor de recomendación."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models import (
    RecomendacionesAvanzadasResponse,
    RecomendacionesResponse,
    UsuariosInfluyentesResponse,
)
from app.repositories import consultas as consultas_repo


router = APIRouter()


# ============================================
# RECOMENDACIONES (caso de uso principal)
# ============================================


@router.get(
    "/recomendaciones/{usuario_id}",
    response_model=RecomendacionesResponse,
    tags=["Recomendaciones"],
    summary="Recomendaciones personalizadas (likes + vistas + seguidos)",
)
def recomendaciones(
    usuario_id: str,
    limit: int = Query(10, ge=1, le=50, description="Máximo de series a sugerir"),
    genero: Optional[str] = Query(None, description="Filtrar por nombre de género"),
    plataforma: Optional[str] = Query(None, description="Filtrar por nombre de plataforma"),
    anio: Optional[int] = Query(None, description="Filtrar por año de la serie"),
):
    """Motor de recomendación basado en likes/vistas del usuario y de quienes sigue.

    Soporta filtros opcionales por género, plataforma y año.
    Rúbrica: Consulta Cypher — caso de uso principal (con filtros).
    """
    if not consultas_repo.usuario_existe(usuario_id):
        raise HTTPException(status_code=404, detail=f"Usuario {usuario_id} no encontrado")

    items = consultas_repo.recomendaciones_para_usuario(
        usuario_id, limit=limit, genero=genero, plataforma=plataforma, anio=anio
    )
    return {"usuario_id": usuario_id, "total": len(items), "items": items}


@router.get(
    "/recomendaciones/{usuario_id}/avanzado",
    response_model=RecomendacionesAvanzadasResponse,
    tags=["Recomendaciones"],
    summary="Motor de recomendación HÍBRIDO (Jaccard)",
)
def recomendaciones_avanzadas(
    usuario_id: str,
    limit: int = Query(10, ge=1, le=50),
    w_jaccard: float = Query(1.0, ge=0),
    w_genero: float = Query(0.5, ge=0),
    w_social: float = Query(0.4, ge=0),
    w_popularidad: float = Query(0.2, ge=0),
    w_novedad: float = Query(0.3, ge=0),
):
    """Sistema de recomendación híbrido con Jaccard Similarity y desglose explicable."""
    if not consultas_repo.usuario_existe(usuario_id):
        raise HTTPException(status_code=404, detail=f"Usuario {usuario_id} no encontrado")

    items = consultas_repo.recomendaciones_avanzadas(
        usuario_id=usuario_id,
        limit=limit,
        w_jaccard=w_jaccard,
        w_genero=w_genero,
        w_social=w_social,
        w_popularidad=w_popularidad,
        w_novedad=w_novedad,
    )
    return {
        "usuario_id": usuario_id,
        "algoritmo": "hybrid_jaccard",
        "pesos": {
            "w_jaccard": w_jaccard,
            "w_genero": w_genero,
            "w_social": w_social,
            "w_popularidad": w_popularidad,
            "w_novedad": w_novedad,
        },
        "total": len(items),
        "items": items,
    }


# ============================================
# CONSULTAS ANALÍTICAS
# ============================================


@router.get(
    "/consultas/series-mejor-calificadas-por-genero",
    tags=["Consultas"],
    summary="Top series por género (Persona 1)",
)
def series_mejor_calificadas_por_genero():
    return consultas_repo.series_mejor_calificadas_por_genero()


@router.get(
    "/consultas/plataformas-mas-exclusivas",
    tags=["Consultas"],
    summary="Plataformas con mayor porcentaje de contenido exclusivo (Persona 1)",
)
def plataformas_mas_exclusivas():
    return consultas_repo.plataformas_mas_exclusivas()


@router.get(
    "/consultas/top-series",
    tags=["Consultas"],
    summary="Top series por calificación (filtro opcional por género)",
)
def top_series(
    genero: Optional[str] = Query(None, description="Filtrar por nombre de género"),
    limit: int = Query(10, ge=1, le=50),
):
    """Top global de series por calificación. Si se pasa `genero`, restringe al género."""
    items = consultas_repo.top_series(genero=genero, limit=limit)
    return {"genero": genero, "total": len(items), "items": items}


@router.get(
    "/consultas/usuarios-influyentes",
    response_model=UsuariosInfluyentesResponse,
    tags=["Consultas"],
    summary="Top usuarios con más seguidores y reseñas",
)
def usuarios_influyentes(
    limit: int = Query(10, ge=1, le=50, description="Cantidad de usuarios en el top"),
):
    items = consultas_repo.usuarios_influyentes(limit=limit)
    return {"total": len(items), "items": items}


@router.get(
    "/consultas/top-actores",
    tags=["Consultas"],
    summary="Top de actores por número de series y popularidad",
)
def top_actores(limit: int = Query(10, ge=1, le=50)):
    """Devuelve los actores más activos (incluye flag `es_director`)."""
    items = consultas_repo.top_actores(limit=limit)
    return {"total": len(items), "items": items}


@router.get(
    "/consultas/actores-que-tambien-dirigen",
    tags=["Consultas"],
    summary="Actores con multi-label :Director (actúan y dirigen)",
)
def actores_que_tambien_dirigen(limit: int = Query(20, ge=1, le=100)):
    """Demuestra el uso del multi-label `:Actor:Director` en una consulta."""
    items = consultas_repo.actores_que_tambien_dirigen(limit=limit)
    return {"total": len(items), "items": items}
