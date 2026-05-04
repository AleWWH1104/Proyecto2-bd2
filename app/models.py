"""Schemas Pydantic para validación de requests y responses.

Aquí van todos los modelos de datos que usa la API.
Se llenarán conforme se vayan creando las entidades.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date


# ============================================
# SCHEMAS DE NODOS
# ============================================

# Aquí irán: SerieCreate, SerieUpdate, SerieResponse,
#            UsuarioCreate, ActorCreate, GeneroCreate, etc.


# ============================================
# SCHEMAS DE RELACIONES
# ============================================

# Aquí irán: PerteneceA, Transmite, Vio, LeGusta, etc.


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
    """Para eliminar propiedades específicas."""
    nombres: List[str] = Field(..., description="Nombres de las propiedades a eliminar")


class EliminarPropiedadesMasivoRequest(BaseModel):
    """Para eliminar propiedades en múltiples nodos."""
    ids: List[str]
    nombres: List[str]
