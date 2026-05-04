"""Router para Consultas Cypher — Personas 1, 2 y 3.

Persona 1:
    GET /consultas/series-mejor-calificadas-por-genero
    GET /consultas/plataformas-mas-exclusivas
"""

from fastapi import APIRouter
from app import repositories

router = APIRouter(prefix="/consultas", tags=["Consultas"])


# ============================================
# PERSONA 1
# ============================================


@router.get(
    "/series-mejor-calificadas-por-genero",
    summary="Top series por género (Persona 1)",
)
def series_mejor_calificadas_por_genero():
    """Devuelve las series mejor calificadas agrupadas por género.

    Incluye: género, top 5 series, promedio de calificación, cantidad evaluada.
    """
    return repositories.consultas.series_mejor_calificadas_por_genero()


@router.get(
    "/plataformas-mas-exclusivas",
    summary="Plataformas con mayor porcentaje de contenido exclusivo (Persona 1)",
)
def plataformas_mas_exclusivas():
    """Devuelve plataformas ordenadas por porcentaje de series exclusivas.

    Incluye: plataforma, total exclusivas, total series, porcentaje exclusivas.
    """
    return repositories.consultas.plataformas_mas_exclusivas()
