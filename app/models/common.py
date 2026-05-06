"""Schemas genéricos compartidos por varias entidades."""
from pydantic import BaseModel, Field
from typing import List


class IdsRequest(BaseModel):
    """Para operaciones que reciben múltiples IDs."""
    ids: List[str] = Field(..., description="Lista de IDs")


class PropiedadesRequest(BaseModel):
    """Para agregar/actualizar propiedades."""
    propiedades: dict = Field(..., description="Diccionario de propiedades")


class EliminarPropiedadesRequest(BaseModel):
    """Para eliminar propiedades específicas."""
    nombres: List[str] = Field(..., description="Nombres de propiedades a eliminar")


class EliminarPropiedadesMasivoRequest(BaseModel):
    """Para eliminar propiedades de múltiples nodos a la vez."""
    ids: List[str] = Field(..., description="IDs de los nodos")
    nombres: List[str] = Field(..., description="Nombres de propiedades a eliminar")