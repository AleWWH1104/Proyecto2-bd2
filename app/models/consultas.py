"""Schemas para los endpoints de consultas.

Estos schemas describen la forma del response — los inputs llegan como
query params, no llevan body.
"""
from pydantic import BaseModel
from typing import List


class SerieRecomendada(BaseModel):
    """Una serie sugerida al usuario por el motor de recomendación."""
    serie_id: str
    titulo: str
    usuarios_similares: int
    muestra_usuarios: List[str]


class RecomendacionesResponse(BaseModel):
    """Lista de series recomendadas para un usuario."""
    usuario_id: str
    total: int
    items: List[SerieRecomendada]


class UsuarioInfluyente(BaseModel):
    """Un usuario en el ranking de influencia."""
    usuario_id: str
    nombre: str
    seguidores: int
    resenas: int
    influencia: int


class UsuariosInfluyentesResponse(BaseModel):
    """Top de usuarios influyentes."""
    total: int
    items: List[UsuarioInfluyente]
