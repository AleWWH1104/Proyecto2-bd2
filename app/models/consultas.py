"""Schemas para los endpoints de consultas.

Estos schemas describen la forma del response — los inputs llegan como
query params, no llevan body.
"""
from pydantic import BaseModel, Field
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


# ============================================
# Motor avanzado (algoritmo de Data Science)
# ============================================

class SerieRecomendadaAvanzada(BaseModel):
    """Sugerencia del motor híbrido con desglose del score por señal.

    El desglose es clave para *explicabilidad*: el cliente puede mostrar
    al usuario "te lo recomendamos porque comparte 3 géneros con tus
    favoritos y a 5 personas que sigues les gustó".
    """
    serie_id: str
    titulo: str
    score: float
    score_jaccard: float = Field(..., description="Similitud colaborativa (Jaccard sumado)")
    bonus_genero: int = Field(..., description="Géneros de la serie que también están en tus favoritos")
    bonus_social: int = Field(..., description="Likes de gente que sigues")
    popularidad: int = Field(..., description="Total de likes de la serie")
    novedad: float = Field(..., description="Decay exponencial por antigüedad (0..1)")
    coincidencias: int = Field(..., description="Otros usuarios con gustos similares que la likean")


class PesosUsados(BaseModel):
    """Pesos aplicados al scoring híbrido (devueltos para tuning)."""
    w_jaccard: float
    w_genero: float
    w_social: float
    w_popularidad: float
    w_novedad: float


class RecomendacionesAvanzadasResponse(BaseModel):
    """Resultado del motor de recomendación avanzado."""
    usuario_id: str
    algoritmo: str = "hybrid_jaccard"
    pesos: PesosUsados
    total: int
    items: List[SerieRecomendadaAvanzada]
