"""Schemas Pydantic para validación de requests y responses.

Todos los modelos de datos que usa la API.
Naming ASCII según seed.py: anio, puntuacion, Resena, ACTUA_EN, ESCRIBIO.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import date


# ============================================
# SCHEMAS DE SERIE
# ============================================


class SerieBase(BaseModel):
    titulo: str
    sinopsis: str
    anio: int
    calificacion: float
    numTemporadas: int
    numEpisodios: int
    estadoEmision: bool
    activa: bool


class SerieCreate(SerieBase):
    pass


class SeriePatch(BaseModel):
    """Para agregar/actualizar propiedades de una o varias series."""

    propiedades: dict = Field(..., description="Propiedades a agregar o actualizar")


class SeriesMasivoPatchRequest(BaseModel):
    ids: List[str]
    propiedades: dict


class SerieResponse(BaseModel):
    id: str
    titulo: str
    sinopsis: str
    anio: int
    calificacion: float
    numTemporadas: int
    numEpisodios: int
    estadoEmision: bool
    activa: bool


class SerieDetalleResponse(SerieResponse):
    generos: List[dict] = []
    plataformas: List[dict] = []
    similares: List[dict] = []


class SerieListItem(BaseModel):
    id: str
    titulo: str
    anio: int
    calificacion: float
    activa: bool


# ============================================
# SCHEMAS DE FILTROS Y AGREGACIONES DE SERIE
# ============================================


class ConteoPorNombre(BaseModel):
    nombre: str
    total: int


class SeriesAggregations(BaseModel):
    total: int
    promedio_calificacion: Optional[float] = None
    por_genero: List[ConteoPorNombre] = []
    por_plataforma: List[ConteoPorNombre] = []


class SerieListResponse(BaseModel):
    series: List[SerieListItem]
    agregaciones: SeriesAggregations


# ============================================
# SCHEMAS DE GENERO
# ============================================


class GeneroBase(BaseModel):
    nombre: str
    descripcion: str
    popularidad: float
    tendencia: bool
    anio: int


class GeneroCreate(GeneroBase):
    pass


class GeneroResponse(BaseModel):
    id: str
    nombre: str
    descripcion: str
    popularidad: float
    tendencia: bool
    anio: int


# ============================================
# SCHEMAS DE PLATAFORMA
# ============================================


class PlataformaBase(BaseModel):
    nombre: str
    pais: str
    precio: float
    fechaFundacion: date
    suscriptores: int


class PlataformaCreate(PlataformaBase):
    pass


class PlataformaResponse(BaseModel):
    id: str
    nombre: str
    pais: str
    precio: float
    fechaFundacion: date
    suscriptores: int


# ============================================
# SCHEMAS DE RELACIONES
# ============================================


class PerteneceABase(BaseModel):
    esPrincipal: bool
    relevancia: float
    fechaAsignacion: date


class PerteneceACreate(PerteneceABase):
    pass


class PerteneceAPatch(BaseModel):
    propiedades: dict = Field(
        ..., description="Propiedades a actualizar en la relación PERTENECE_A"
    )


class TransmiteCreate(BaseModel):
    fechaDisponible: date
    exclusiva: bool
    regiones: List[str]


class SimilarACreate(BaseModel):
    puntuacionSimilitud: float
    algoritmo: str
    fechaCalculada: date


# ============================================
# SCHEMAS DE OPERACIONES MASIVAS
# ============================================


class IdsRequest(BaseModel):
    """Para operaciones que reciben múltiples IDs."""

    ids: List[str] = Field(..., description="Lista de IDs de nodos")


class PropiedadesRequest(BaseModel):
    """Para agregar/actualizar propiedades de un nodo o relación."""

    propiedades: dict = Field(..., description="Diccionario de propiedades")


class PropiedadesMasivoRequest(BaseModel):
    """Para actualizar propiedades en múltiples nodos a la vez."""

    ids: List[str]
    propiedades: dict


class EliminarPropiedadesRequest(BaseModel):
    """Para eliminar propiedades específicas de un nodo."""

    nombres: List[str] = Field(..., description="Nombres de las propiedades a eliminar")


class EliminarPropiedadesMasivoRequest(BaseModel):
    """Para eliminar propiedades en múltiples nodos."""

    ids: List[str]
    nombres: List[str]
