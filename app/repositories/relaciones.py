"""Repository para Relaciones — Persona 1.

Gestión de relaciones centradas en Serie:
  - PERTENECE_A  (Serie → Genero)
  - TRANSMITE    (Plataforma → Serie)
  - SIMILAR_A    (Serie → Serie)

Regla: siempre validar que los nodos existan antes de crear la relación.
"""

from typing import Optional
from app.database import get_session


# ============================================
# PERTENECE_A  (Serie)-[:PERTENECE_A]->(Genero)
# ============================================


def crear_pertenece_a(serie_id: str, genero_id: str, data: dict) -> dict:
    """Crea la relación PERTENECE_A con 3 propiedades.

    Valida que tanto la Serie como el Genero existan.
    """
    fecha = data.get("fechaAsignacion")
    if hasattr(fecha, "isoformat"):
        data["fechaAsignacion"] = fecha.isoformat()

    query = """
        MATCH (s:Serie {id: $serie_id})
        MATCH (g:Genero {id: $genero_id})
        CREATE (s)-[r:PERTENECE_A {
            esPrincipal: $esPrincipal,
            relevancia: $relevancia,
            fechaAsignacion: date($fechaAsignacion)
        }]->(g)
        RETURN s.id AS serie_id, g.id AS genero_id,
               r.esPrincipal AS esPrincipal,
               r.relevancia AS relevancia,
               r.fechaAsignacion AS fechaAsignacion
    """
    params = {
        "serie_id": serie_id,
        "genero_id": genero_id,
        **data,
    }
    with get_session() as session:
        result = session.run(query, params)
        record = result.single()
        if not record:
            return None
        row = dict(record)
        for k, v in row.items():
            if hasattr(v, "iso_format"):
                row[k] = v.iso_format()
        return row


def actualizar_pertenece_a(serie_id: str, genero_id: str, propiedades: dict) -> Optional[dict]:
    """Actualiza propiedades de la relación PERTENECE_A."""
    # Manejar fechas dentro de propiedades
    for k, v in propiedades.items():
        if hasattr(v, "isoformat"):
            propiedades[k] = v.isoformat()

    # SET r += $propiedades no maneja fechas Cypher; construimos la query dinámicamente
    set_parts = []
    params = {"serie_id": serie_id, "genero_id": genero_id}
    for key, value in propiedades.items():
        if key == "fechaAsignacion":
            set_parts.append(f"r.{key} = date(${key})")
        else:
            set_parts.append(f"r.{key} = ${key}")
        params[key] = value

    if not set_parts:
        return None

    set_clause = "SET " + ", ".join(set_parts)
    query = f"""
        MATCH (s:Serie {{id: $serie_id}})-[r:PERTENECE_A]->(g:Genero {{id: $genero_id}})
        {set_clause}
        RETURN s.id AS serie_id, g.id AS genero_id,
               r.esPrincipal AS esPrincipal,
               r.relevancia AS relevancia,
               r.fechaAsignacion AS fechaAsignacion
    """
    with get_session() as session:
        result = session.run(query, params)
        record = result.single()
        if not record:
            return None
        row = dict(record)
        for k, v in row.items():
            if hasattr(v, "iso_format"):
                row[k] = v.iso_format()
        return row


def eliminar_pertenece_a(serie_id: str, genero_id: str) -> bool:
    """Elimina la relación PERTENECE_A entre una Serie y un Genero."""
    query = """
        MATCH (s:Serie {id: $serie_id})-[r:PERTENECE_A]->(g:Genero {id: $genero_id})
        DELETE r
        RETURN count(r) AS eliminadas
    """
    with get_session() as session:
        result = session.run(query, {"serie_id": serie_id, "genero_id": genero_id})
        record = result.single()
        return bool(record and record["eliminadas"] > 0)


# ============================================
# TRANSMITE  (Plataforma)-[:TRANSMITE]->(Serie)
# ============================================


def crear_transmite(plataforma_id: str, serie_id: str, data: dict) -> dict:
    """Crea la relación TRANSMITE con 3 propiedades.

    Valida que tanto la Plataforma como la Serie existan.
    """
    fecha = data.get("fechaDisponible")
    if hasattr(fecha, "isoformat"):
        data["fechaDisponible"] = fecha.isoformat()

    # regiones es lista — la pasamos tal cual
    query = """
        MATCH (p:Plataforma {id: $plataforma_id})
        MATCH (s:Serie {id: $serie_id})
        CREATE (p)-[r:TRANSMITE {
            fechaDisponible: date($fechaDisponible),
            exclusiva: $exclusiva,
            regiones: $regiones
        }]->(s)
        RETURN p.id AS plataforma_id, s.id AS serie_id,
               r.fechaDisponible AS fechaDisponible,
               r.exclusiva AS exclusiva,
               r.regiones AS regiones
    """
    params = {
        "plataforma_id": plataforma_id,
        "serie_id": serie_id,
        **data,
    }
    with get_session() as session:
        result = session.run(query, params)
        record = result.single()
        if not record:
            return None
        row = dict(record)
        for k, v in row.items():
            if hasattr(v, "iso_format"):
                row[k] = v.iso_format()
        return row


# ============================================
# SIMILAR_A  (Serie)-[:SIMILAR_A]->(Serie)
# ============================================


def crear_similar_a(serie1_id: str, serie2_id: str, data: dict) -> dict:
    """Crea la relación SIMILAR_A con 3 propiedades.

    Valida que ambas Series existan.
    """
    fecha = data.get("fechaCalculada")
    if hasattr(fecha, "isoformat"):
        data["fechaCalculada"] = fecha.isoformat()

    query = """
        MATCH (s1:Serie {id: $serie1_id})
        MATCH (s2:Serie {id: $serie2_id})
        CREATE (s1)-[r:SIMILAR_A {
            puntuacionSimilitud: $puntuacionSimilitud,
            algoritmo: $algoritmo,
            fechaCalculada: date($fechaCalculada)
        }]->(s2)
        RETURN s1.id AS serie1_id, s2.id AS serie2_id,
               r.puntuacionSimilitud AS puntuacionSimilitud,
               r.algoritmo AS algoritmo,
               r.fechaCalculada AS fechaCalculada
    """
    params = {
        "serie1_id": serie1_id,
        "serie2_id": serie2_id,
        **data,
    }
    with get_session() as session:
        result = session.run(query, params)
        record = result.single()
        if not record:
            return None
        row = dict(record)
        for k, v in row.items():
            if hasattr(v, "iso_format"):
                row[k] = v.iso_format()
        return row
