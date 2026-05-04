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
    RecomendacionesAvanzadasResponse,
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


# ============================================
# Algoritmo de Data Science (extra de la rúbrica)
# ============================================
# OJO: este path es más específico que /usuarios/{usuario_id}/recomendaciones,
# pero FastAPI los enruta sin conflicto porque difieren en el último segmento.

@router.get(
    "/usuarios/{usuario_id}/recomendaciones/avanzado",
    response_model=RecomendacionesAvanzadasResponse,
    tags=["Consultas"],
    summary="Motor de recomendación HÍBRIDO (Jaccard + género + social + popularidad + novedad)",
)
def recomendaciones_avanzadas(
    usuario_id: str,
    limit: int = Query(10, ge=1, le=50),
    w_jaccard: float = Query(1.0, ge=0, description="Peso del filtrado colaborativo (Jaccard)"),
    w_genero: float = Query(0.5, ge=0, description="Peso del overlap de géneros"),
    w_social: float = Query(0.4, ge=0, description="Peso de likes de gente que sigue"),
    w_popularidad: float = Query(0.2, ge=0, description="Peso de la popularidad global"),
    w_novedad: float = Query(0.3, ge=0, description="Peso de la novedad (decay por antigüedad)"),
):
    """Sistema de recomendación híbrido con **Jaccard Similarity**.

    Implementa un *weighted hybrid recommender* — patrón clásico en Data Science.
    Combina filtrado colaborativo (Jaccard) con señales de contenido, sociales,
    popularidad y novedad. Los pesos de cada señal se pueden tunear vía query
    params para experimentar.

    **Sobre Jaccard**: medida de similitud entre conjuntos definida como
    `J(A, B) = |A ∩ B| / |A ∪ B|`. Aplicada aquí entre los conjuntos de
    series que le gustan a dos usuarios. Es el algoritmo de DS que se cita
    en el reporte académico.

    Cada item del response trae el desglose por señal para *explicabilidad*
    del modelo.
    """
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
