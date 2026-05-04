"""Schemas de Persona 1: Series, catálogos y agregaciones."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


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
    propiedades: dict = Field(..., description="Propiedades a agregar o actualizar")


class SeriesMasivoPatchRequest(BaseModel):
    ids: list[str]
    propiedades: dict


class SerieResponse(SerieBase):
    id: str


class SerieDetalleResponse(SerieResponse):
    generos: list[dict] = Field(default_factory=list)
    plataformas: list[dict] = Field(default_factory=list)
    similares: list[dict] = Field(default_factory=list)


class SerieListItem(BaseModel):
    id: str
    titulo: str
    anio: int
    calificacion: float
    activa: bool


class ConteoPorNombre(BaseModel):
    nombre: str
    total: int


class SeriesAggregations(BaseModel):
    total: int
    promedio_calificacion: Optional[float] = None
    por_genero: list[ConteoPorNombre] = Field(default_factory=list)
    por_plataforma: list[ConteoPorNombre] = Field(default_factory=list)


class SerieListResponse(BaseModel):
    series: list[SerieListItem]
    agregaciones: SeriesAggregations


class GeneroBase(BaseModel):
    nombre: str
    descripcion: str
    popularidad: float
    tendencia: bool
    anio: int


class GeneroCreate(GeneroBase):
    pass


class GeneroResponse(GeneroBase):
    id: str


class PlataformaBase(BaseModel):
    nombre: str
    pais: str
    precio: float
    fechaFundacion: date
    suscriptores: int


class PlataformaCreate(PlataformaBase):
    pass


class PlataformaResponse(PlataformaBase):
    id: str
