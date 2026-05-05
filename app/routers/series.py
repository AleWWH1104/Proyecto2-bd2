"""Router para Series.

Endpoints:
    GET    /series                    - Listar con filtros y agregaciones
    GET    /series/{id}               - Detalle con relaciones
    POST   /series                    - Crear con propiedades
    PATCH  /series/masivo             - Actualizar propiedades en varias series
    PATCH  /series/{id}               - Actualizar/agregar propiedades de 1 serie
    DELETE /series/{id}/propiedades   - Eliminar propiedades específicas
    DELETE /series/masivo             - Eliminar múltiples series (DETACH DELETE masivo)
    DELETE /series/{id}               - Eliminar 1 serie (DETACH DELETE)
    GET    /series/{id}/similares     - Series similares (SIMILAR_A)
    GET    /series/{id}/resenas       - Reseñas de una serie
    POST   /series/{id}/resenas       - Crear reseña sobre una serie
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
    ResenaCreatePorSerie,
    ResenaResponse,
    ResenasListResponse,
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
    genero: Optional[str] = Query(None, description="Nombre del género para filtrar"),
    plataforma: Optional[str] = Query(None, description="Nombre de la plataforma para filtrar"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de resultados"),
    skip: int = Query(0, ge=0, description="Desplazamiento para paginación"),
):
    """Lista series con filtros opcionales + bloque de agregaciones.

    Acepta filtros por id (`genero_id`, `plataforma_id`) o por nombre (`genero`, `plataforma`).
    """
    return repositories.series.listar_series(
        titulo=titulo,
        anio=anio,
        calificacion_min=calificacion_min,
        calificacion_max=calificacion_max,
        activa=activa,
        estadoEmision=estadoEmision,
        genero_id=genero_id,
        plataforma_id=plataforma_id,
        genero=genero,
        plataforma=plataforma,
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


# IMPORTANTE: /masivo debe ir ANTES de /{serie_id} para que FastAPI no
# interprete "masivo" como un serie_id.
@router.delete("/masivo", summary="Eliminar múltiples series")
def eliminar_series_masivo(body: IdsRequest):
    """Elimina múltiples Series y sus relaciones (DETACH DELETE masivo).

    Rúbrica: Eliminar múltiples nodos.
    """
    eliminadas = repositories.series.eliminar_series(body.ids)
    return {"eliminadas": eliminadas, "ids": body.ids}


@router.delete("/{serie_id}", summary="Eliminar una serie")
def eliminar_serie(serie_id: str):
    """Elimina una Serie y todas sus relaciones (DETACH DELETE)."""
    ok = repositories.series.eliminar_serie(serie_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Serie '{serie_id}' no encontrada")
    return {"mensaje": f"Serie '{serie_id}' eliminada correctamente"}


# ============================================
# SIMILARES DE UNA SERIE
# ============================================


@router.get(
    "/{serie_id}/similares",
    summary="Series similares a esta",
)
def listar_series_similares(
    serie_id: str,
    limit: int = Query(10, ge=1, le=50),
):
    """Devuelve series similares según la relación SIMILAR_A.

    Rúbrica: Consulta Cypher — series similares.
    """
    items = repositories.consultas.series_similares(serie_id, limit=limit)
    if items is None:
        raise HTTPException(status_code=404, detail=f"Serie '{serie_id}' no encontrada")
    return {"serie_id": serie_id, "total": len(items), "items": items}


# ============================================
# RESEÑAS DE UNA SERIE
# ============================================


@router.get(
    "/{serie_id}/resenas",
    response_model=ResenasListResponse,
    summary="Ver reseñas de una serie",
)
def listar_resenas_de_serie(
    serie_id: str,
    puntuacion_min: Optional[int] = Query(None, ge=1, le=10),
    puntuacion_max: Optional[int] = Query(None, ge=1, le=10),
    contiene_spoilers: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """Lista las reseñas de una serie con filtros opcionales.

    Rúbrica: Consultar muchos nodos + filtros.
    """
    return repositories.resenas.listar(
        serie_id=serie_id,
        puntuacion_min=puntuacion_min,
        puntuacion_max=puntuacion_max,
        contiene_spoilers=contiene_spoilers,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/{serie_id}/resenas",
    response_model=ResenaResponse,
    status_code=201,
    summary="Escribir reseña sobre una serie",
)
def crear_resena_de_serie(serie_id: str, datos: ResenaCreatePorSerie):
    """Crea Resena + relación ESCRIBIO + relación SOBRE en una sola operación.

    Rúbrica: Crear nodo + relaciones.
    """
    resena = repositories.resenas.crear(
        usuario_id=datos.usuario_id,
        serie_id=serie_id,
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
            detail=f"Usuario {datos.usuario_id} o Serie {serie_id} no encontrado",
        )
    return resena
