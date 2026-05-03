"""Router para series.

Define los endpoints HTTP de esta entidad.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/series", tags=["series"])


# Endpoints a implementar (revisar lista completa en el documento de spec)
