"""Paquete de repositorios.

Expone cada módulo de repositorio para que los routers puedan
usar: from app import repositories; repositories.series.listar_series(...)
"""

from app.repositories import (
    series,
    relaciones,
    consultas,
    actores,
    estudios,
    usuarios,
    resenas,
)
