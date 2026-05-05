"""Schemas de relaciones de Persona 1 y Persona 2."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


# ============================================
# PERSONA 1
# ============================================


class PerteneceABase(BaseModel):
    esPrincipal: bool
    relevancia: float
    fechaAsignacion: date


class PerteneceACreate(PerteneceABase):
    pass


class PerteneceAPatch(BaseModel):
    propiedades: dict = Field(..., description="Propiedades a actualizar en PERTENECE_A")


class TransmiteCreate(BaseModel):
    fechaDisponible: date
    exclusiva: bool
    regiones: list[str]


class SimilarACreate(BaseModel):
    puntuacionSimilitud: float
    algoritmo: str
    fechaCalculada: date


# ============================================
# PERSONA 2
# ============================================


class VioCreate(BaseModel):
    porcentajeVisto: float = Field(..., ge=0, le=100)
    completada: bool = Field(default=False)
    calificacion: Optional[float] = Field(default=None, ge=0, le=10)


class VioPatch(BaseModel):
    """Body para PATCH /usuarios/{uid}/vio/{sid}. Todos los campos son opcionales."""
    porcentajeVisto: Optional[float] = Field(default=None, ge=0, le=100)
    completada: Optional[bool] = None
    calificacion: Optional[float] = Field(default=None, ge=0, le=10)


class VioMasivoItem(BaseModel):
    serie_id: str
    porcentajeVisto: Optional[float] = Field(default=None, ge=0, le=100)
    completada: Optional[bool] = None
    calificacion: Optional[float] = Field(default=None, ge=0, le=10)


class VioMasivoUpdate(BaseModel):
    items: list[VioMasivoItem] = Field(..., min_length=1)


class LeGustaCreate(BaseModel):
    puntuacion: Optional[int] = Field(default=None, ge=1, le=5)
    notificarx: Optional[bool] = Field(default=True)


class LeGustaEliminarMasivo(BaseModel):
    serie_ids: list[str] = Field(..., min_length=1)


class EnListaCreate(BaseModel):
    prioridad: Optional[int] = Field(default=3, ge=1, le=5)
    notificaciones: Optional[bool] = Field(default=True)


class SigueACreate(BaseModel):
    notificaciones: Optional[bool] = Field(default=True)


class RelacionResponse(BaseModel):
    mensaje: str
    relacion: dict


class OperacionMasivaResponse(BaseModel):
    mensaje: str
    afectados: int
