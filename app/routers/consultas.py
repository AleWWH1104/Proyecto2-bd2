"""Router para consultas.

Define los endpoints HTTP de esta entidad.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/consultas", tags=["consultas"])


# Endpoints a implementar (revisar lista completa en el documento de spec)
