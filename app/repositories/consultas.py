"""Repository para consultas analíticas y de recomendación.

Combina las consultas de Persona 1 y Persona 2.
"""
from typing import Optional

from app.database import get_session
from app.repositories._helpers import to_native


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


def recomendaciones_para_usuario(
    usuario_id: str,
    limit: int = 10,
    genero: Optional[str] = None,
    plataforma: Optional[str] = None,
    anio: Optional[int] = None,
) -> list[dict]:
    """Filtrado colaborativo: usa likes + vistas + seguidos del usuario.

    Filtros opcionales por nombre de género, nombre de plataforma o año.
    """
    extra_filtros = []
    params: dict = {"usuario_id": usuario_id, "limit": limit}

    if genero is not None:
        extra_filtros.append(
            "EXISTS { MATCH (rec)-[:PERTENECE_A]->(g:Genero) WHERE g.nombre = $genero }"
        )
        params["genero"] = genero
    if plataforma is not None:
        extra_filtros.append(
            "EXISTS { MATCH (p:Plataforma {nombre: $plataforma})-[:TRANSMITE]->(rec) }"
        )
        params["plataforma"] = plataforma
    if anio is not None:
        extra_filtros.append("rec.anio = $anio")
        params["anio"] = anio

    extra_where = ("AND " + " AND ".join(extra_filtros)) if extra_filtros else ""

    # Une 3 señales: usuarios afines (likes/vistas) + usuarios seguidos
    query = f"""
        MATCH (u:Usuario {{id: $usuario_id}})
        OPTIONAL MATCH (u)-[:LE_GUSTA|VIO]->(:Serie)<-[:LE_GUSTA]-(afin:Usuario)
        OPTIONAL MATCH (u)-[:SIGUE_A]->(seguido:Usuario)
        WITH u, collect(DISTINCT afin) + collect(DISTINCT seguido) AS otros
        UNWIND otros AS otro
        WITH u, otro
        WHERE otro IS NOT NULL AND otro.id <> u.id
        MATCH (otro)-[:LE_GUSTA]->(rec:Serie)
        WHERE NOT (u)-[:VIO]->(rec)
          AND NOT (u)-[:LE_GUSTA]->(rec)
          AND NOT (u)-[:EN_LISTA]->(rec)
          {extra_where}
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
        result = session.run(query, params)
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
        OPTIONAL MATCH (u)-[:LE_GUSTA|VIO]->(s_u:Serie)
        WITH u, collect(DISTINCT s_u) AS likes_u

        MATCH (rec:Serie)
        WHERE NOT (u)-[:VIO]->(rec)
          AND NOT (u)-[:LE_GUSTA]->(rec)
          AND NOT (u)-[:EN_LISTA]->(rec)

        OPTIONAL MATCH (otro:Usuario)-[:LE_GUSTA|VIO]->(rec)
        WHERE otro <> u
        OPTIONAL MATCH (otro)-[:LE_GUSTA|VIO]->(s_o:Serie)
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
                WHEN rec.anio IS NULL THEN 0.5
                WHEN rec.anio >= date().year THEN 1.0
                ELSE exp(-toFloat(date().year - rec.anio) / 5.0)
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


def top_series(genero: Optional[str] = None, limit: int = 10) -> list[dict]:
    """Top de series por calificación, opcionalmente filtradas por género."""
    if genero is not None:
        query = """
            MATCH (s:Serie)-[:PERTENECE_A]->(g:Genero {nombre: $genero})
            WITH s
            OPTIONAL MATCH (s)-[:PERTENECE_A]->(go:Genero)
            RETURN s.id AS serie_id,
                   s.titulo AS titulo,
                   s.calificacion AS calificacion,
                   s.anio AS anio,
                   collect(DISTINCT go.nombre) AS generos
            ORDER BY s.calificacion DESC, s.titulo ASC
            LIMIT $limit
        """
        params = {"genero": genero, "limit": limit}
    else:
        query = """
            MATCH (s:Serie)
            OPTIONAL MATCH (s)-[:PERTENECE_A]->(g:Genero)
            RETURN s.id AS serie_id,
                   s.titulo AS titulo,
                   s.calificacion AS calificacion,
                   s.anio AS anio,
                   collect(DISTINCT g.nombre) AS generos
            ORDER BY s.calificacion DESC, s.titulo ASC
            LIMIT $limit
        """
        params = {"limit": limit}

    with get_session() as session:
        result = session.run(query, params)
        return [
            {
                "serie_id": r["serie_id"],
                "titulo": r["titulo"],
                "calificacion": r["calificacion"],
                "anio": r["anio"],
                "generos": list(r["generos"]),
            }
            for r in result
        ]


def top_actores(limit: int = 10) -> list[dict]:
    """Top de actores por número de series y popularidad."""
    query = """
        MATCH (a:Actor)
        OPTIONAL MATCH (a)-[:ACTUA_EN]->(s:Serie)
        WITH a, count(DISTINCT s) AS series_count
        RETURN a.id AS actor_id,
               a.nombre AS nombre,
               a.popularidad AS popularidad,
               a.premios AS premios,
               series_count,
               'Director' IN labels(a) AS es_director
        ORDER BY series_count DESC, a.popularidad DESC
        LIMIT $limit
    """
    with get_session() as session:
        result = session.run(query, limit=limit)
        return [dict(record) for record in result]


def actores_que_tambien_dirigen(limit: int = 20) -> list[dict]:
    """Actores con multi-label :Director — actúan y además dirigen.

    Demuestra el uso del multi-label en una consulta.
    """
    query = """
        MATCH (a:Actor:Director)
        OPTIONAL MATCH (a)-[:ACTUA_EN]->(serie_act:Serie)
        OPTIONAL MATCH (a)-[:DIRIGE]->(serie_dir:Serie)
        WITH a,
             count(DISTINCT serie_act) AS series_actuadas,
             count(DISTINCT serie_dir) AS series_dirigidas,
             collect(DISTINCT serie_dir.titulo)[0..5] AS muestra_dirigidas
        RETURN a.id AS actor_id,
               a.nombre AS nombre,
               a.nacionalidad AS nacionalidad,
               series_actuadas,
               series_dirigidas,
               (series_actuadas + series_dirigidas) AS total,
               muestra_dirigidas
        ORDER BY total DESC, series_dirigidas DESC
        LIMIT $limit
    """
    with get_session() as session:
        result = session.run(query, limit=limit)
        return [
            {
                "actor_id": r["actor_id"],
                "nombre": r["nombre"],
                "nacionalidad": r["nacionalidad"],
                "series_actuadas": r["series_actuadas"],
                "series_dirigidas": r["series_dirigidas"],
                "total": r["total"],
                "muestra_dirigidas": list(r["muestra_dirigidas"]),
            }
            for r in result
        ]


def series_similares(serie_id: str, limit: int = 10) -> Optional[list[dict]]:
    """Series similares a una dada (relación SIMILAR_A).

    Devuelve None si la serie no existe; lista (vacía o no) si existe.
    """
    existe_query = "MATCH (s:Serie {id: $id}) RETURN s LIMIT 1"
    query = """
        MATCH (s:Serie {id: $id})-[r:SIMILAR_A]->(sim:Serie)
        OPTIONAL MATCH (sim)-[:PERTENECE_A]->(g:Genero)
        RETURN sim.id AS serie_id,
               sim.titulo AS titulo,
               sim.calificacion AS calificacion,
               r.puntuacionSimilitud AS puntuacion_similitud,
               r.algoritmo AS algoritmo,
               collect(DISTINCT g.nombre) AS generos
        ORDER BY r.puntuacionSimilitud DESC
        LIMIT $limit
    """
    with get_session() as session:
        if session.run(existe_query, id=serie_id).single() is None:
            return None
        result = session.run(query, id=serie_id, limit=limit)
        return [
            {
                "serie_id": r["serie_id"],
                "titulo": r["titulo"],
                "calificacion": r["calificacion"],
                "puntuacion_similitud": r["puntuacion_similitud"],
                "algoritmo": r["algoritmo"],
                "generos": list(r["generos"]),
            }
            for r in result
        ]
