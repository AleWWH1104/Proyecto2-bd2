"""Repository para Plataformas.

Queries Cypher para listar y crear plataformas.
"""

import uuid
from typing import List
from app.database import get_session


def listar_plataformas() -> List[dict]:
    """Retorna todos los nodos Plataforma."""
    query = """
        MATCH (p:Plataforma)
        RETURN p
        ORDER BY p.nombre
    """
    with get_session() as session:
        result = session.run(query)
        plataformas = []
        for record in result:
            p = dict(record["p"])
            for k, v in p.items():
                if hasattr(v, "iso_format"):
                    p[k] = v.iso_format()
            plataformas.append(p)
        return plataformas


def crear_plataforma(data: dict) -> dict:
    """Crea un nodo Plataforma con todas sus propiedades."""
    plataforma_id = str(uuid.uuid4())
    # fechaFundacion puede venir como date object o string
    fecha = data.get("fechaFundacion")
    if hasattr(fecha, "isoformat"):
        data["fechaFundacion"] = fecha.isoformat()

    query = """
        CREATE (p:Plataforma {
            id: $id,
            nombre: $nombre,
            pais: $pais,
            precio: $precio,
            fechaFundacion: date($fechaFundacion),
            suscriptores: $suscriptores
        })
        RETURN p
    """
    params = {"id": plataforma_id, **data}
    with get_session() as session:
        result = session.run(query, params)
        record = result.single()
        p = dict(record["p"])
        for k, v in p.items():
            if hasattr(v, "iso_format"):
                p[k] = v.iso_format()
        return p
