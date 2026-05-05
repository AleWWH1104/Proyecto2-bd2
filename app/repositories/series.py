"""Repository para Series.

Queries Cypher para todas las operaciones CRUD de Series.
Fuente de verdad del contrato: scripts/seed.py y docs/grafo.md
"""

import uuid
from typing import Optional, List
from app.database import get_session


def _record_to_serie(record, key: str = "s") -> dict:
    """Convierte un Record de Neo4j a dict serializable."""
    node = record[key]
    data = dict(node)
    # Convertir fechas a string si vienen como Date de Neo4j
    for k, v in data.items():
        if hasattr(v, "iso_format"):
            data[k] = v.iso_format()
    return data


def listar_series(
    titulo: Optional[str] = None,
    anio: Optional[int] = None,
    calificacion_min: Optional[float] = None,
    calificacion_max: Optional[float] = None,
    activa: Optional[bool] = None,
    estadoEmision: Optional[bool] = None,
    genero_id: Optional[str] = None,
    plataforma_id: Optional[str] = None,
    genero: Optional[str] = None,
    plataforma: Optional[str] = None,
    limit: int = 20,
    skip: int = 0,
) -> dict:
    """Lista series con filtros opcionales y devuelve agregaciones.

    Acepta filtros por id (`genero_id`, `plataforma_id`) o por nombre (`genero`, `plataforma`).
    """
    conditions = []
    params: dict = {"limit": limit, "skip": skip}

    if titulo:
        conditions.append("toLower(s.titulo) CONTAINS toLower($titulo)")
        params["titulo"] = titulo
    if anio is not None:
        conditions.append("s.anio = $anio")
        params["anio"] = anio
    if calificacion_min is not None:
        conditions.append("s.calificacion >= $calificacion_min")
        params["calificacion_min"] = calificacion_min
    if calificacion_max is not None:
        conditions.append("s.calificacion <= $calificacion_max")
        params["calificacion_max"] = calificacion_max
    if activa is not None:
        conditions.append("s.activa = $activa")
        params["activa"] = activa
    if estadoEmision is not None:
        conditions.append("s.estadoEmision = $estadoEmision")
        params["estadoEmision"] = estadoEmision
    if genero_id:
        conditions.append("EXISTS { MATCH (s)-[:PERTENECE_A]->(g2:Genero {id: $genero_id}) }")
        params["genero_id"] = genero_id
    if plataforma_id:
        conditions.append("EXISTS { MATCH (p2:Plataforma {id: $plataforma_id})-[:TRANSMITE]->(s) }")
        params["plataforma_id"] = plataforma_id
    if genero:
        conditions.append("EXISTS { MATCH (s)-[:PERTENECE_A]->(g3:Genero {nombre: $genero}) }")
        params["genero"] = genero
    if plataforma:
        conditions.append("EXISTS { MATCH (p3:Plataforma {nombre: $plataforma})-[:TRANSMITE]->(s) }")
        params["plataforma"] = plataforma

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = f"""
        MATCH (s:Serie)
        {where_clause}
        WITH s
        ORDER BY s.calificacion DESC
        SKIP $skip LIMIT $limit
        OPTIONAL MATCH (s)-[:PERTENECE_A]->(g:Genero)
        OPTIONAL MATCH (p:Plataforma)-[:TRANSMITE]->(s)
        RETURN s,
               collect(DISTINCT g.nombre) AS generos,
               collect(DISTINCT p.nombre) AS plataformas
    """

    # Query de agregaciones (total, promedio, conteos)
    agg_query = f"""
        MATCH (s:Serie)
        {where_clause}
        WITH s
        OPTIONAL MATCH (s)-[:PERTENECE_A]->(g:Genero)
        OPTIONAL MATCH (p:Plataforma)-[:TRANSMITE]->(s)
        RETURN
            count(DISTINCT s) AS total,
            avg(s.calificacion) AS promedio_calificacion,
            collect(DISTINCT g.nombre) AS generos_list,
            collect(DISTINCT p.nombre) AS plataformas_list
    """

    # Query de conteo por genero
    genero_count_query = f"""
        MATCH (s:Serie)
        {where_clause}
        OPTIONAL MATCH (s)-[:PERTENECE_A]->(g:Genero)
        WHERE g IS NOT NULL
        RETURN g.nombre AS nombre, count(DISTINCT s) AS total
        ORDER BY total DESC
    """

    # Query de conteo por plataforma
    plataforma_count_query = f"""
        MATCH (s:Serie)
        {where_clause}
        OPTIONAL MATCH (p:Plataforma)-[:TRANSMITE]->(s)
        WHERE p IS NOT NULL
        RETURN p.nombre AS nombre, count(DISTINCT s) AS total
        ORDER BY total DESC
    """

    with get_session() as session:
        # Series paginadas
        result = session.run(query, params)
        series = []
        for record in result:
            s = dict(record["s"])
            series.append(
                {
                    "id": s.get("id"),
                    "titulo": s.get("titulo"),
                    "anio": s.get("anio"),
                    "calificacion": s.get("calificacion"),
                    "activa": s.get("activa"),
                }
            )

        # Agregaciones
        agg_result = session.run(agg_query, params)
        agg_record = agg_result.single()
        total = agg_record["total"] if agg_record else 0
        promedio = agg_record["promedio_calificacion"] if agg_record else None

        # Conteo por genero
        gen_result = session.run(genero_count_query, params)
        por_genero = [{"nombre": r["nombre"], "total": r["total"]} for r in gen_result]

        # Conteo por plataforma
        plat_result = session.run(plataforma_count_query, params)
        por_plataforma = [{"nombre": r["nombre"], "total": r["total"]} for r in plat_result]

    return {
        "series": series,
        "agregaciones": {
            "total": total,
            "promedio_calificacion": promedio,
            "por_genero": por_genero,
            "por_plataforma": por_plataforma,
        },
    }


def obtener_serie_por_id(serie_id: str) -> Optional[dict]:
    """Retorna una serie con sus relaciones (géneros, plataformas, similares)."""
    query = """
        MATCH (s:Serie {id: $id})
        OPTIONAL MATCH (s)-[:PERTENECE_A]->(g:Genero)
        OPTIONAL MATCH (p:Plataforma)-[:TRANSMITE]->(s)
        OPTIONAL MATCH (s)-[:SIMILAR_A]->(sim:Serie)
        RETURN s,
               collect(DISTINCT {id: g.id, nombre: g.nombre}) AS generos,
               collect(DISTINCT {id: p.id, nombre: p.nombre}) AS plataformas,
               collect(DISTINCT {id: sim.id, titulo: sim.titulo}) AS similares
    """
    with get_session() as session:
        result = session.run(query, {"id": serie_id})
        record = result.single()
        if not record:
            return None
        s = dict(record["s"])
        return {
            **s,
            "generos": [g for g in record["generos"] if g.get("id")],
            "plataformas": [p for p in record["plataformas"] if p.get("id")],
            "similares": [sim for sim in record["similares"] if sim.get("id")],
        }


def crear_serie(data: dict) -> dict:
    """Crea un nodo Serie con todas sus propiedades."""
    serie_id = str(uuid.uuid4())
    query = """
        CREATE (s:Serie {
            id: $id,
            titulo: $titulo,
            sinopsis: $sinopsis,
            anio: $anio,
            calificacion: $calificacion,
            numTemporadas: $numTemporadas,
            numEpisodios: $numEpisodios,
            estadoEmision: $estadoEmision,
            activa: $activa
        })
        RETURN s
    """
    params = {"id": serie_id, **data}
    with get_session() as session:
        result = session.run(query, params)
        record = result.single()
        return dict(record["s"])


def actualizar_propiedades_serie(serie_id: str, propiedades: dict) -> Optional[dict]:
    """Agrega o actualiza propiedades de una Serie."""
    query = """
        MATCH (s:Serie {id: $id})
        SET s += $propiedades
        RETURN s
    """
    with get_session() as session:
        result = session.run(query, {"id": serie_id, "propiedades": propiedades})
        record = result.single()
        if not record:
            return None
        return dict(record["s"])


def actualizar_propiedades_series_masivo(ids: list, propiedades: dict) -> int:
    """Agrega o actualiza propiedades en múltiples Series a la vez."""
    query = """
        UNWIND $ids AS serie_id
        MATCH (s:Serie {id: serie_id})
        SET s += $propiedades
        RETURN count(s) AS actualizadas
    """
    with get_session() as session:
        result = session.run(query, {"ids": ids, "propiedades": propiedades})
        record = result.single()
        return record["actualizadas"] if record else 0


def eliminar_propiedades_serie(serie_id: str, nombres: list) -> Optional[dict]:
    """Elimina propiedades específicas de una Serie (no borra el nodo)."""
    # Construir la cláusula REMOVE dinámicamente
    remove_parts = [f"s.`{nombre}`" for nombre in nombres]
    remove_clause = "REMOVE " + ", ".join(remove_parts)
    query = f"""
        MATCH (s:Serie {{id: $id}})
        {remove_clause}
        RETURN s
    """
    with get_session() as session:
        result = session.run(query, {"id": serie_id})
        record = result.single()
        if not record:
            return None
        return dict(record["s"])


def eliminar_serie(serie_id: str) -> bool:
    """Elimina una Serie y todas sus relaciones (DETACH DELETE)."""
    query = """
        MATCH (s:Serie {id: $id})
        DETACH DELETE s
        RETURN count(s) AS eliminadas
    """
    with get_session() as session:
        result = session.run(query, {"id": serie_id})
        record = result.single()
        return bool(record and record["eliminadas"] > 0)


def eliminar_series(ids: list) -> int:
    """Elimina múltiples Series y sus relaciones (DETACH DELETE masivo)."""
    query = """
        UNWIND $ids AS serie_id
        MATCH (s:Serie {id: serie_id})
        DETACH DELETE s
        RETURN count(s) AS eliminadas
    """
    with get_session() as session:
        result = session.run(query, {"ids": ids})
        record = result.single()
        return record["eliminadas"] if record else 0
