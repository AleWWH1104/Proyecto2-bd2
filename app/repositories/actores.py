"""Repository para Actores (con soporte multi-label :Actor:Director)
y la relación ACTUA_EN.
"""
import uuid
from typing import Optional

from app.database import get_session
from app.repositories._helpers import to_native


def _generar_id() -> str:
    return f"act_{uuid.uuid4().hex[:8]}"


def _serializar_actor(record) -> dict:
    """Aplana el record (a, labels) en un dict listo para Pydantic."""
    actor = dict(record["a"])
    return to_native({**actor, "labels": list(record["labels"])})


def crear(data: dict) -> dict:
    """Crea un Actor. Si data['es_director'] es True, se crea con multi-label.

    Rúbrica: Crear nodo 2+ labels (multi-label).
    """
    es_director = bool(data.pop("es_director", False))
    actor_id = _generar_id()
    fecha = data["fechaNacimiento"]
    fecha_iso = fecha.isoformat() if hasattr(fecha, "isoformat") else fecha

    # Cypher es estático sobre los labels: ramificamos la query
    if es_director:
        query = """
            CREATE (a:Actor:Director {
                id: $id,
                nombre: $nombre,
                nacionalidad: $nacionalidad,
                fechaNacimiento: date($fechaNacimiento),
                premios: $premios,
                activo: $activo,
                popularidad: $popularidad,
                papeles: $papeles
            })
            RETURN a, labels(a) AS labels
        """
    else:
        query = """
            CREATE (a:Actor {
                id: $id,
                nombre: $nombre,
                nacionalidad: $nacionalidad,
                fechaNacimiento: date($fechaNacimiento),
                premios: $premios,
                activo: $activo,
                popularidad: $popularidad,
                papeles: $papeles
            })
            RETURN a, labels(a) AS labels
        """

    params = {
        "id": actor_id,
        "nombre": data["nombre"],
        "nacionalidad": data["nacionalidad"],
        "fechaNacimiento": fecha_iso,
        "premios": data["premios"],
        "activo": data["activo"],
        "popularidad": data["popularidad"],
        "papeles": data["papeles"],
    }
    with get_session() as session:
        record = session.run(query, params).single()
        return _serializar_actor(record)


def agregar_label_director(actor_id: str) -> Optional[dict]:
    """Agrega el label :Director a un Actor existente (multi-label dinámico).

    Devuelve el actor actualizado o None si no existe.
    """
    query = """
        MATCH (a:Actor {id: $id})
        SET a:Director
        RETURN a, labels(a) AS labels
    """
    with get_session() as session:
        record = session.run(query, id=actor_id).single()
        if record is None:
            return None
        return _serializar_actor(record)


def crear_actua_en(actor_id: str, serie_id: str, data: dict) -> Optional[dict]:
    """Crea la relación ACTUA_EN entre Actor y Serie con propiedades."""
    query = """
        MATCH (a:Actor {id: $actor_id})
        MATCH (s:Serie {id: $serie_id})
        CREATE (a)-[r:ACTUA_EN {
            personaje: $personaje,
            protagonista: $protagonista,
            temporadas: $temporadas
        }]->(s)
        RETURN a.id AS actor_id, s.id AS serie_id,
               r.personaje AS personaje,
               r.protagonista AS protagonista,
               r.temporadas AS temporadas
    """
    with get_session() as session:
        record = session.run(
            query,
            actor_id=actor_id,
            serie_id=serie_id,
            personaje=data["personaje"],
            protagonista=data["protagonista"],
            temporadas=data["temporadas"],
        ).single()
        if record is None:
            return None
        return to_native(dict(record))


def actualizar_actua_en(
    actor_id: str,
    serie_id: str,
    propiedades: dict,
) -> Optional[dict]:
    """Actualiza propiedades de ACTUA_EN. Filtra valores None."""
    props = {k: v for k, v in propiedades.items() if v is not None}
    query = """
        MATCH (a:Actor {id: $actor_id})-[r:ACTUA_EN]->(s:Serie {id: $serie_id})
        SET r += $props
        RETURN a.id AS actor_id, s.id AS serie_id,
               r.personaje AS personaje,
               r.protagonista AS protagonista,
               r.temporadas AS temporadas
    """
    with get_session() as session:
        record = session.run(
            query, actor_id=actor_id, serie_id=serie_id, props=props
        ).single()
        if record is None:
            return None
        return to_native(dict(record))


def eliminar_actua_en(actor_id: str, serie_id: str) -> bool:
    """Elimina la relación ACTUA_EN entre Actor y Serie."""
    query = """
        MATCH (a:Actor {id: $actor_id})-[r:ACTUA_EN]->(s:Serie {id: $serie_id})
        DELETE r
        RETURN count(r) AS eliminadas
    """
    with get_session() as session:
        record = session.run(
            query, actor_id=actor_id, serie_id=serie_id
        ).single()
        return bool(record and record["eliminadas"] > 0)
