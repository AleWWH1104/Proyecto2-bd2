"""Repository para Generos.

Queries Cypher para listar y crear géneros.
"""

import uuid
from typing import List, Optional
from app.database import get_session


def listar_generos() -> List[dict]:
    """Retorna todos los nodos Genero."""
    query = """
        MATCH (g:Genero)
        RETURN g
        ORDER BY g.nombre
    """
    with get_session() as session:
        result = session.run(query)
        generos = []
        for record in result:
            g = dict(record["g"])
            for k, v in g.items():
                if hasattr(v, "iso_format"):
                    g[k] = v.iso_format()
            generos.append(g)
        return generos


def crear_genero(data: dict) -> dict:
    """Crea un nodo Genero con todas sus propiedades."""
    genero_id = str(uuid.uuid4())
    query = """
        CREATE (g:Genero {
            id: $id,
            nombre: $nombre,
            descripcion: $descripcion,
            popularidad: $popularidad,
            tendencia: $tendencia,
            anio: $anio
        })
        RETURN g
    """
    params = {"id": genero_id, **data}
    with get_session() as session:
        result = session.run(query, params)
        record = result.single()
        return dict(record["g"])
