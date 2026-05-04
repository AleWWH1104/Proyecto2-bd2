"""Schemas de las relaciones del Usuario.

Cubre las relaciones del nodo Usuario hacia otros nodos:
- Usuario→Serie:   VIO, LE_GUSTA, EN_LISTA
- Usuario→Usuario: SIGUE_A
"""
from pydantic import BaseModel, Field
from typing import List, Optional


# ============================================
# Usuario -[VIO]-> Serie
# ============================================

class VioCreate(BaseModel):
    """Body para POST /usuarios/{usuario_id}/vio/{serie_id}."""
    porcentajeVisto: float = Field(..., ge=0, le=100)
    completada: bool = Field(default=False)
    calificacion: Optional[float] = Field(default=None, ge=0, le=10)


class VioMasivoItem(BaseModel):
    """Un item dentro del update masivo de VIO."""
    serie_id: str
    porcentajeVisto: Optional[float] = Field(default=None, ge=0, le=100)
    completada: Optional[bool] = None
    calificacion: Optional[float] = Field(default=None, ge=0, le=10)


class VioMasivoUpdate(BaseModel):
    """Body para PATCH /usuarios/{usuario_id}/vio-masivo."""
    items: List[VioMasivoItem] = Field(..., min_length=1)


# ============================================
# Usuario -[LE_GUSTA]-> Serie
# ============================================

class LeGustaCreate(BaseModel):
    """Body para POST /usuarios/{usuario_id}/le-gusta/{serie_id}."""
    puntuacion: Optional[int] = Field(default=None, ge=1, le=5)
    notificarx: Optional[bool] = Field(default=True)


class LeGustaEliminarMasivo(BaseModel):
    """Body para DELETE /usuarios/{usuario_id}/le-gusta-masivo."""
    serie_ids: List[str] = Field(..., min_length=1)


# ============================================
# Usuario -[EN_LISTA]-> Serie
# ============================================

class EnListaCreate(BaseModel):
    """Body para POST /usuarios/{usuario_id}/en-lista/{serie_id}."""
    prioridad: Optional[int] = Field(default=3, ge=1, le=5)
    notificaciones: Optional[bool] = Field(default=True)


# ============================================
# Usuario -[SIGUE_A]-> Usuario
# ============================================

class SigueACreate(BaseModel):
    """Body para POST /usuarios/{usuario_id}/sigue/{otro_usuario_id}."""
    notificaciones: Optional[bool] = Field(default=True)


# ============================================
# Response genérica de relación
# ============================================

class RelacionResponse(BaseModel):
    """Respuesta estándar para operaciones sobre relaciones."""
    mensaje: str
    relacion: dict


class OperacionMasivaResponse(BaseModel):
    """Respuesta para operaciones masivas (cuántos se afectaron)."""
    mensaje: str
    afectados: int
