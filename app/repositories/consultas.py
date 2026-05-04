"""Repository para consultas analíticas y de recomendación.

Combina las consultas de Persona 1 y Persona 2.
"""

from app.database import get_session


# ============================================
# PERSONA 1
# ============================================


def series_mejor_calificadas_por_genero() -> list:
    """Top series por género ordenadas por calificación promedio."""
    query = """
        MATCH (s:Serie)-[:PERTENECE_A]->(g:Genero)
        WITH g, s
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
        return [
            {
                "genero_id": record["genero_id"],
                "genero": record["genero"],
                "top_series": list(record["top_series"]),
                "promedio_calificacion": record["promedio_calificacion"],
                "cantidad_series": record["cantidad_series"],
            }
            for record in result
        ]


def plataformas_mas_exclusivas() -> list:
    """Plataformas ordenadas por porcentaje de series exclusivas."""
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
        return [
            {
                "plataforma_id": record["plataforma_id"],
                "plataforma": record["plataforma"],
                "total_exclusivas": record["total_exclusivas"],
                "total_series": record["total_series"],
                "porcentaje_exclusivas": record["porcentaje_exclusivas"],
            }
            for record in result
        ]


# ============================================
# PERSONA 2
# ============================================


def recomendaciones_para_usuario(usuario_id: str, limit: int = 10) -> list[dict]:
    """Filtrado colaborativo básico."""
    query = """
        MATCH (u:Usuario {id: $usuario_id})-[:LE_GUSTA]->(:Serie)<-[:LE_GUSTA]-(otro:Usuario)
        WHERE otro.id <> u.id
        MATCH (otro)-[:LE_GUSTA]->(rec:Serie)
        WHERE NOT (u)-[:VIO]->(rec)
          AND NOT (u)-[:LE_GUSTA]->(rec)
          AND NOT (u)-[:EN_LISTA]->(rec)
        WITH rec,
             count(DISTINCT otro) AS usuarios_similares,
             collect(DISTINCT otro.nombre)[0..5] AS muestra_usuarios
        RETURN rec.id AS serie_id,
               rec.titulo AS titulo,
               usuarios_similares,
               muestra_usuarios
        ORDER BY usuarios_similares DESC
        LIMIT $limit
    """
    with get_session() as session:
        result = session.run(query, usuario_id=usuario_id, limit=limit)
        return [dict(record) for record in result]


def usuario_existe(usuario_id: str) -> bool:
    query = "MATCH (u:Usuario {id: $id}) RETURN u LIMIT 1"
    with get_session() as session:
        return session.run(query, id=usuario_id).single() is not None


def recomendaciones_avanzadas(
    usuario_id: str,
    limit: int = 10,
    w_jaccard: float = 1.0,
    w_genero: float = 0.5,
    w_social: float = 0.4,
    w_popularidad: float = 0.2,
    w_novedad: float = 0.3,
) -> list[dict]:
    """Sistema de recomendación híbrido con Jaccard Similarity."""
    query = """
        MATCH (u:Usuario {id: $usuario_id})
        OPTIONAL MATCH (u)-[:LE_GUSTA]->(s_u:Serie)
        WITH u, collect(DISTINCT s_u) AS likes_u

        MATCH (rec:Serie)
        WHERE NOT (u)-[:VIO]->(rec)
          AND NOT (u)-[:LE_GUSTA]->(rec)
          AND NOT (u)-[:EN_LISTA]->(rec)

        OPTIONAL MATCH (otro:Usuario)-[:LE_GUSTA]->(rec)
        WHERE otro <> u
        OPTIONAL MATCH (otro)-[:LE_GUSTA]->(s_o:Serie)
        WITH u, likes_u, rec, otro, collect(DISTINCT s_o) AS likes_otro

        WITH u, likes_u, rec, otro, likes_otro,
             [s IN likes_otro WHERE s IN likes_u] AS interseccion
        WITH u, likes_u, rec, otro,
             CASE
                WHEN size(likes_u) = 0 OR size(likes_otro) = 0 THEN 0.0
                ELSE toFloat(size(interseccion)) /
                     (size(likes_u) + size(likes_otro) - size(interseccion))
             END AS jaccard_uo

        WITH u, likes_u, rec, otro, jaccard_uo,
             CASE
                WHEN otro IS NOT NULL AND exists((u)-[:SIGUE_A]->(otro)) THEN 1
                ELSE 0
             END AS es_seguido

        WITH u, likes_u, rec,
             sum(jaccard_uo) AS score_jaccard,
             sum(es_seguido) AS bonus_social,
             count(otro) AS coincidencias

        OPTIONAL MATCH (rec)-[:PERTENECE_A]->(g:Genero)<-[:PERTENECE_A]-(s_match:Serie)
        WHERE s_match IN likes_u
        WITH rec, score_jaccard, bonus_social, coincidencias,
             count(DISTINCT g) AS bonus_genero

        OPTIONAL MATCH (rec)<-[:LE_GUSTA]-(:Usuario)
        WITH rec, score_jaccard, bonus_social, coincidencias, bonus_genero,
             count(*) AS popularidad

        WITH rec, score_jaccard, bonus_social, coincidencias, bonus_genero, popularidad,
             CASE
                WHEN rec.fechaLanzamiento IS NULL THEN 0.5
                ELSE exp(-toFloat(date().year - rec.fechaLanzamiento.year) / 5.0)
             END AS novedad

        WITH rec, score_jaccard, bonus_genero, bonus_social, coincidencias,
             popularidad, novedad,
             ($w_jaccard * score_jaccard) +
             ($w_genero  * toFloat(bonus_genero)) +
             ($w_social  * toFloat(bonus_social)) +
             ($w_pop     * log(popularidad + 1)) +
             ($w_novedad * novedad) AS score

        WHERE score > 0
        RETURN rec.id AS serie_id,
               rec.titulo AS titulo,
               round(score * 1000) / 1000.0 AS score,
               round(score_jaccard * 1000) / 1000.0 AS score_jaccard,
               bonus_genero,
               bonus_social,
               popularidad,
               round(novedad * 1000) / 1000.0 AS novedad,
               coincidencias
        ORDER BY score DESC
        LIMIT $limit
    """
    with get_session() as session:
        result = session.run(
            query,
            usuario_id=usuario_id,
            limit=limit,
            w_jaccard=w_jaccard,
            w_genero=w_genero,
            w_social=w_social,
            w_pop=w_popularidad,
            w_novedad=w_novedad,
        )
        return [dict(record) for record in result]


def usuarios_influyentes(limit: int = 10) -> list[dict]:
    """Top de usuarios por influencia."""
    query = """
        MATCH (u:Usuario)
        OPTIONAL MATCH (u)<-[:SIGUE_A]-(seguidor:Usuario)
        OPTIONAL MATCH (u)-[:ESCRIBIO]->(r:Resena)
        WITH u,
             count(DISTINCT seguidor) AS seguidores,
             count(DISTINCT r) AS resenas
        RETURN u.id AS usuario_id,
               u.nombre AS nombre,
               seguidores,
               resenas,
               (seguidores * 2 + resenas) AS influencia
        ORDER BY influencia DESC, seguidores DESC
        LIMIT $limit
    """
    with get_session() as session:
        result = session.run(query, limit=limit)
        return [dict(record) for record in result]
