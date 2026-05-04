"""Router para consultas analíticas y motor de recomendación."""

from fastapi import APIRouter, HTTPException, Query

from app.models import (
    RecomendacionesAvanzadasResponse,
    RecomendacionesResponse,
    UsuariosInfluyentesResponse,
)
from app.repositories import consultas as consultas_repo


router = APIRouter()


# ============================================
# PERSONA 1
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


# ============================================
# PERSONA 2
# ============================================


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
    items = consultas_repo.usuarios_influyentes(limit=limit)
    return {"total": len(items), "items": items}


@router.get(
    "/usuarios/{usuario_id}/recomendaciones/avanzado",
    response_model=RecomendacionesAvanzadasResponse,
    tags=["Consultas"],
    summary="Motor de recomendación HÍBRIDO",
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
