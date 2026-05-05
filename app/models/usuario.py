"""Schemas de Usuario."""
from pydantic import BaseModel, Field
from typing import List
from datetime import date


class UsuarioCreate(BaseModel):
    """Body para POST /usuarios."""
    nombre: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=5)
    edad: int = Field(..., ge=13, le=120)
    activo: bool = Field(default=True)


class UsuarioPatch(BaseModel):
    """Body para PATCH /usuarios/{id}. Propiedades a agregar o actualizar."""
    propiedades: dict = Field(..., description="Propiedades a agregar o actualizar")


class UsuarioResponse(BaseModel):
    """Datos básicos de un usuario en respuestas."""
    id: str
    nombre: str
    email: str
    edad: int
    fechaRegistro: date
    activo: bool


class UsuarioPerfilCompleto(BaseModel):
    """Perfil con todas las relaciones del usuario."""
    usuario: UsuarioResponse
    series_vistas: List[dict] = Field(default_factory=list)
    series_que_le_gustan: List[dict] = Field(default_factory=list)
    series_en_lista: List[dict] = Field(default_factory=list)
    usuarios_que_sigue: List[dict] = Field(default_factory=list)
    resenas: List[dict] = Field(default_factory=list)


class UsuariosListResponse(BaseModel):
    """Respuesta paginada de usuarios."""
    total: int
    items: List[UsuarioResponse]