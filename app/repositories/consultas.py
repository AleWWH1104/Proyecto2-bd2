"""Repository para consultas analíticas / de recomendación.

Queries que combinan varios nodos y relaciones para responder preguntas
de negocio (no son CRUD de una entidad puntual).
"""
from app.database import get_session


def recomendaciones_para_usuario(usuario_id: str, limit: int = 10) -> list[dict]:
    """Filtrado colaborativo: series que les gustan a usuarios que comparten
    gustos con el usuario, excluyendo lo que el usuario ya conoce.

    Lógica:
    1. Buscar otros usuarios que también dieron LE_GUSTA a series que al usuario le gustan.
    2. Tomar las series que les gustan a esos usuarios "similares".
    3. Excluir las que el usuario ya VIO, le gustan o tiene EN_LISTA.
    4. Rankear por cantidad de usuarios similares que las recomiendan.
    """
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
    """Helper para distinguir 'usuario sin recomendaciones' de 'usuario inexistente'."""
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
    """Sistema de recomendación HÍBRIDO con Jaccard Similarity.

    Combina 5 señales en un score final por serie candidata:
      1. score_jaccard  → suma de Jaccard(usuario, otro) para cada otro
                           que likeó la serie. Jaccard = |A∩B| / |A∪B|.
      2. bonus_genero   → cuántos géneros de la serie aparecen entre los
                           géneros que ya le gustan al usuario.
      3. bonus_social   → cuánta gente que sigue le dio like a la serie.
      4. popularidad    → log(total_likes + 1), suaviza colas largas.
      5. novedad        → exp(-años / 5), favorece series recientes.

    El score final es una combinación lineal con pesos configurables:
      score = Σ(w_i * señal_i)

    Filtra series ya vistas/likeadas/en lista del usuario.

    Cold-start: si el usuario no tiene likes, score_jaccard=0 y
    bonus_genero=0 → la recomendación cae a popularidad + novedad
    (fallback razonable para usuarios nuevos).
    """
    query = """
        // 1. Perfil del usuario: sus likes
        MATCH (u:Usuario {id: $usuario_id})
        OPTIONAL MATCH (u)-[:LE_GUSTA]->(s_u:Serie)
        WITH u, collect(DISTINCT s_u) AS likes_u

        // 2. Candidatos: series que el usuario aún no conoce
        MATCH (rec:Serie)
        WHERE NOT (u)-[:VIO]->(rec)
          AND NOT (u)-[:LE_GUSTA]->(rec)
          AND NOT (u)-[:EN_LISTA]->(rec)

        // 3. Para cada otro usuario que likeó rec, calcular Jaccard(u, otro)
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

        // 4. ¿u sigue a otro?  → bonus social
        WITH u, likes_u, rec, otro, jaccard_uo,
             CASE
                WHEN otro IS NOT NULL AND exists((u)-[:SIGUE_A]->(otro)) THEN 1
                ELSE 0
             END AS es_seguido

        // 5. Agregar todas las contribuciones de "otros" en una sola fila por rec
        WITH u, likes_u, rec,
             sum(jaccard_uo) AS score_jaccard,
             sum(es_seguido) AS bonus_social,
             count(otro)     AS coincidencias

        // 6. Bonus de género: géneros de rec que también están en los gustos
        OPTIONAL MATCH (rec)-[:PERTENECE_A]->(g:Genero)<-[:PERTENECE_A]-(s_match:Serie)
        WHERE s_match IN likes_u
        WITH rec, score_jaccard, bonus_social, coincidencias,
             count(DISTINCT g) AS bonus_genero

        // 7. Popularidad de rec (cuántos likes en total)
        OPTIONAL MATCH (rec)<-[:LE_GUSTA]-(:Usuario)
        WITH rec, score_jaccard, bonus_social, coincidencias, bonus_genero,
             count(*) AS popularidad

        // 8. Novedad: decay exponencial de años desde lanzamiento.
        //     Series sin fechaLanzamiento → 0.5 (neutral, no se penalizan).
        WITH rec, score_jaccard, bonus_social, coincidencias, bonus_genero, popularidad,
             CASE
                WHEN rec.fechaLanzamiento IS NULL THEN 0.5
                ELSE exp(-toFloat(date().year - rec.fechaLanzamiento.year) / 5.0)
             END AS novedad

        // 9. Score final = combinación lineal de señales
        WITH rec, score_jaccard, bonus_genero, bonus_social, coincidencias,
             popularidad, novedad,
             ($w_jaccard * score_jaccard) +
             ($w_genero  * toFloat(bonus_genero)) +
             ($w_social  * toFloat(bonus_social)) +
             ($w_pop     * log(popularidad + 1)) +
             ($w_novedad * novedad) AS score

        WHERE score > 0
        RETURN rec.id    AS serie_id,
               rec.titulo AS titulo,
               round(score * 1000) / 1000.0          AS score,
               round(score_jaccard * 1000) / 1000.0  AS score_jaccard,
               bonus_genero,
               bonus_social,
               popularidad,
               round(novedad * 1000) / 1000.0        AS novedad,
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
    """Top de usuarios por influencia.

    Influencia = seguidores * 2 + reseñas escritas.
    Los seguidores pesan más que las reseñas (criterio editorial: tener audiencia
    es más relevante que producir contenido para definir 'influencia').
    """
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
