"""Repository para Consultas Cypher — Personas 1, 2 y 3.

Persona 1:
  - series_mejor_calificadas_por_genero
  - plataformas_mas_exclusivas

Persona 2 y 3 agregarán sus funciones aquí conforme avancen.
"""

from app.database import get_session


# ============================================
# PERSONA 1 — Consulta 1
# GET /consultas/series-mejor-calificadas-por-genero
# ============================================


def series_mejor_calificadas_por_genero() -> list:
    """Top series por género ordenadas por calificación promedio.

    Usa: MATCH, WITH, ORDER BY, AVG, COUNT.
    Responde: genero, top_series, promedio_calificacion, cantidad_series.
    """
    query = """
        MATCH (s:Serie)-[:PERTENECE_A]->(g:Genero)
        WITH g,
             s
        ORDER BY s.calificacion DESC
        WITH g,
             collect(s)[0..5] AS top_series,
             avg(s.calificacion) AS promedio_calificacion,
             count(s) AS cantidad_series
        ORDER BY promedio_calificacion DESC
        RETURN
            g.id AS genero_id,
            g.nombre AS genero,
            [ts IN top_series | {id: ts.id, titulo: ts.titulo, calificacion: ts.calificacion}] AS top_series,
            promedio_calificacion,
            cantidad_series
    """
    with get_session() as session:
        result = session.run(query)
        rows = []
        for record in result:
            rows.append(
                {
                    "genero_id": record["genero_id"],
                    "genero": record["genero"],
                    "top_series": list(record["top_series"]),
                    "promedio_calificacion": record["promedio_calificacion"],
                    "cantidad_series": record["cantidad_series"],
                }
            )
        return rows


# ============================================
# PERSONA 1 — Consulta 2
# GET /consultas/plataformas-mas-exclusivas
# ============================================


def plataformas_mas_exclusivas() -> list:
    """Plataformas ordenadas por porcentaje de series exclusivas.

    Usa: MATCH, WHERE r.exclusiva = true, COUNT, ORDER BY.
    Responde: plataforma, total_exclusivas, total_series, porcentaje_exclusivas.
    """
    query = """
        MATCH (p:Plataforma)-[r:TRANSMITE]->(s:Serie)
        WITH p,
             count(s) AS total_series,
             count(CASE WHEN r.exclusiva = true THEN 1 END) AS total_exclusivas
        WHERE total_series > 0
        WITH p,
             total_series,
             total_exclusivas,
             round(100.0 * total_exclusivas / total_series, 2) AS porcentaje_exclusivas
        ORDER BY porcentaje_exclusivas DESC, total_exclusivas DESC
        RETURN
            p.id AS plataforma_id,
            p.nombre AS plataforma,
            total_exclusivas,
            total_series,
            porcentaje_exclusivas
    """
    with get_session() as session:
        result = session.run(query)
        rows = []
        for record in result:
            rows.append(
                {
                    "plataforma_id": record["plataforma_id"],
                    "plataforma": record["plataforma"],
                    "total_exclusivas": record["total_exclusivas"],
                    "total_series": record["total_series"],
                    "porcentaje_exclusivas": record["porcentaje_exclusivas"],
                }
            )
        return rows
