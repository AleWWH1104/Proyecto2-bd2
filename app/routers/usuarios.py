"""Router para usuarios.

Define los endpoints HTTP de esta entidad.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


# Endpoints a implementar (revisar lista completa en el documento de spec)
