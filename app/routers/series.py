"""Router para Series — Persona 1.

Endpoints:
    GET    /series                    - Listar con filtros y agregaciones
    GET    /series/{id}               - Detalle con relaciones
    POST   /series                    - Crear con propiedades
    PATCH  /series/masivo             - Actualizar propiedades en varias series
    PATCH  /series/{id}               - Actualizar/agregar propiedades de 1 serie
    DELETE /series/{id}/propiedades   - Eliminar propiedades específicas
    DELETE /series/{id}               - Eliminar 1 serie (DETACH DELETE)
    DELETE /series                    - Eliminar múltiples series (DETACH DELETE masivo)
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models import (
    SerieCreate,
    SeriePatch,
    SerieResponse,
    SerieDetalleResponse,
    SerieListResponse,
    SeriesMasivoPatchRequest,
    IdsRequest,
    EliminarPropiedadesRequest,
)
from app import repositories

router = APIRouter(prefix="/series", tags=["Series"])


@router.get(
    "", response_model=SerieListResponse, summary="Listar series con filtros y agregaciones"
)
def listar_series(
    titulo: Optional[str] = Query(None, description="Filtrar por título (contiene)"),
    anio: Optional[int] = Query(None, description="Filtrar por año de estreno"),
    calificacion_min: Optional[float] = Query(None, description="Calificación mínima"),
    calificacion_max: Optional[float] = Query(None, description="Calificación máxima"),
    activa: Optional[bool] = Query(None, description="Filtrar por estado activa"),
    estadoEmision: Optional[bool] = Query(None, description="Filtrar por estado de emisión"),
    genero_id: Optional[str] = Query(None, description="ID del género para filtrar"),
    plataforma_id: Optional[str] = Query(None, description="ID de la plataforma para filtrar"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de resultados"),
    skip: int = Query(0, ge=0, description="Desplazamiento para paginación"),
):
    """Lista series con filtros opcionales + bloque de agregaciones."""
    return repositories.series.listar_series(
        titulo=titulo,
        anio=anio,
        calificacion_min=calificacion_min,
        calificacion_max=calificacion_max,
        activa=activa,
        estadoEmision=estadoEmision,
        genero_id=genero_id,
        plataforma_id=plataforma_id,
        limit=limit,
        skip=skip,
    )


@router.get(
    "/{serie_id}", response_model=SerieDetalleResponse, summary="Obtener detalle de una serie"
)
def obtener_serie(serie_id: str):
    """Retorna el detalle completo de una Serie con sus relaciones."""
    serie = repositories.series.obtener_serie_por_id(serie_id)
    if not serie:
        raise HTTPException(status_code=404, detail=f"Serie '{serie_id}' no encontrada")
    return serie


@router.post("", response_model=SerieResponse, status_code=201, summary="Crear una nueva serie")
def crear_serie(data: SerieCreate):
    """Crea un nodo Serie con al menos 9 propiedades configuradas."""
    serie = repositories.series.crear_serie(data.model_dump())
    return serie


@router.patch("/masivo", summary="Actualizar propiedades en múltiples series")
def actualizar_series_masivo(body: SeriesMasivoPatchRequest):
    """Agrega o actualiza propiedades en varias Series a la vez (UNWIND)."""
    actualizadas = repositories.series.actualizar_propiedades_series_masivo(
        body.ids, body.propiedades
    )
    return {"actualizadas": actualizadas, "ids": body.ids}


@router.patch(
    "/{serie_id}", response_model=SerieResponse, summary="Actualizar propiedades de una serie"
)
def actualizar_serie(serie_id: str, body: SeriePatch):
    """Agrega o actualiza propiedades de un nodo Serie."""
    serie = repositories.series.actualizar_propiedades_serie(serie_id, body.propiedades)
    if not serie:
        raise HTTPException(status_code=404, detail=f"Serie '{serie_id}' no encontrada")
    return serie


@router.delete("/{serie_id}/propiedades", summary="Eliminar propiedades específicas de una serie")
def eliminar_propiedades_serie(serie_id: str, body: EliminarPropiedadesRequest):
    """Elimina propiedades específicas de un nodo Serie (no borra el nodo)."""
    serie = repositories.series.eliminar_propiedades_serie(serie_id, body.nombres)
    if not serie:
        raise HTTPException(status_code=404, detail=f"Serie '{serie_id}' no encontrada")
    return {"mensaje": "Propiedades eliminadas", "serie": serie}


@router.delete("/{serie_id}", summary="Eliminar una serie")
def eliminar_serie(serie_id: str):
    """Elimina una Serie y todas sus relaciones (DETACH DELETE)."""
    ok = repositories.series.eliminar_serie(serie_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Serie '{serie_id}' no encontrada")
    return {"mensaje": f"Serie '{serie_id}' eliminada correctamente"}


@router.delete("", summary="Eliminar múltiples series")
def eliminar_series(body: IdsRequest):
    """Elimina múltiples Series y sus relaciones (DETACH DELETE masivo)."""
    eliminadas = repositories.series.eliminar_series(body.ids)
    return {"eliminadas": eliminadas, "ids": body.ids}
