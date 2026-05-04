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
