"""Router para admin.

Define los endpoints HTTP de esta entidad.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])


# Endpoints a implementar (revisar lista completa en el documento de spec)
