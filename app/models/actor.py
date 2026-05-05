"""Schemas de Actor (puede tener multi-label :Actor:Director)."""
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class ActorCreate(BaseModel):
    """Body para POST /actores. Si es_director=True crea con :Actor:Director."""
    nombre: str = Field(..., min_length=1, max_length=150)
    nacionalidad: str = Field(..., min_length=1)
    fechaNacimiento: date
    premios: int = Field(default=0, ge=0)
    activo: bool = True
    popularidad: float = Field(..., ge=0, le=100)
    papeles: List[str] = Field(default_factory=list)
    es_director: bool = Field(default=False, description="Si True, crea multi-label :Actor:Director")


class ActorResponse(BaseModel):
    """Datos de un actor incluyendo sus labels actuales."""
    id: str
    nombre: str
    nacionalidad: str
    fechaNacimiento: date
    premios: int
    activo: bool
    popularidad: float
    papeles: List[str]
    labels: List[str]


class ActuaEnCreate(BaseModel):
    """Body para POST /actores/{aid}/actua-en/{sid}."""
    personaje: str = Field(..., min_length=1)
    protagonista: bool = Field(default=False)
    temporadas: List[int] = Field(default_factory=list)


class ActuaEnPatch(BaseModel):
    """Body para PATCH /actores/{aid}/actua-en/{sid}. Todos opcionales."""
    personaje: Optional[str] = None
    protagonista: Optional[bool] = None
    temporadas: Optional[List[int]] = None
