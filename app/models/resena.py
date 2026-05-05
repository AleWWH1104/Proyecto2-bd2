"""Schemas de Reseña.

La creación de una reseña implica 3 operaciones en el grafo:
- nodo Resena
- relación (Usuario)-[:ESCRIBIO]->(Resena)
- relación (Resena)-[:SOBRE]->(Serie)

Los 3 se hacen en un solo POST.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class ResenaCreate(BaseModel):
    """Body para POST /resenas — crea nodo + ESCRIBIO + SOBRE."""
    usuario_id: str = Field(..., description="Autor de la reseña")
    serie_id: str = Field(..., description="Serie reseñada")
    texto: str = Field(..., min_length=1, max_length=5000)
    puntuacion: int = Field(..., ge=1, le=10)
    etiquetas: List[str] = Field(default_factory=list)

    # Propiedades de la relación ESCRIBIO
    visibilidad: str = Field(default="publica", description="publica | privada | amigos")

    # Propiedades de la relación SOBRE
    contieneSpoilers: bool = Field(default=False)
    temporadaAfectada: Optional[int] = Field(default=None, ge=1)
    protagonista: bool = Field(default=False)


class ResenaCreatePorSerie(BaseModel):
    """Body para POST /series/{id}/resenas — la serie viene del path."""
    usuario_id: str = Field(..., description="Autor de la reseña")
    texto: str = Field(..., min_length=1, max_length=5000)
    puntuacion: int = Field(..., ge=1, le=10)
    etiquetas: List[str] = Field(default_factory=list)
    visibilidad: str = Field(default="publica", description="publica | privada | amigos")
    contieneSpoilers: bool = Field(default=False)
    temporadaAfectada: Optional[int] = Field(default=None, ge=1)
    protagonista: bool = Field(default=False)


class ResenaPatch(BaseModel):
    """Body para PATCH /resenas/{id}. Propiedades del nodo Resena a actualizar."""
    propiedades: dict = Field(..., description="Propiedades a actualizar (texto, puntuacion, etiquetas...)")


class ResenaResponse(BaseModel):
    """Reseña con datos del autor y la serie a la que pertenece."""
    id: str
    texto: str
    puntuacion: int
    fecha: date
    etiquetas: List[str]
    util: int
    usuario_id: str
    serie_id: str
    visibilidad: str
    contieneSpoilers: bool


class ResenasListResponse(BaseModel):
    """Respuesta paginada de reseñas."""
    total: int
    items: List[ResenaResponse]
