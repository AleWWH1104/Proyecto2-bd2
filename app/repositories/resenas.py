"""Repository para reseñas.

Queries Cypher para el nodo Resena y sus dos relaciones:
- (Usuario)-[:ESCRIBIO]->(Resena)
- (Resena)-[:SOBRE]->(Serie)
"""
import uuid
from datetime import date
from typing import Optional

from app.database import get_session
from app.repositories._helpers import to_native


def _generar_id() -> str:
    """Genera un id único para reseña tipo res_xxxxxxxx."""
    return f"res_{uuid.uuid4().hex[:8]}"


def _serializar_resena_completa(record) -> dict:
    """Aplana un record (r, escribio, sobre, usuario_id, serie_id) en un dict plano."""
    r = dict(record["r"])
    escribio = dict(record["escribio"]) if record["escribio"] is not None else {}
    sobre = dict(record["sobre"]) if record["sobre"] is not None else {}
    return to_native({
        **r,
        "usuario_id": record["usuario_id"],
        "serie_id": record["serie_id"],
        "visibilidad": escribio.get("visibilidad", "publica"),
        "contieneSpoilers": sobre.get("contieneSpoilers", False),
    })


def listar(
    usuario_id: Optional[str] = None,
    serie_id: Optional[str] = None,
    puntuacion_min: Optional[int] = None,
    puntuacion_max: Optional[int] = None,
    contiene_spoilers: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
) -> dict:
    """Lista reseñas con filtros y paginación.

    Devuelve: {"total": int, "items": [resena_dict, ...]}
    """
    filtros = []
    params = {"skip": skip, "limit": limit}

    if usuario_id is not None:
        filtros.append("u.id = $usuario_id")
        params["usuario_id"] = usuario_id
    if serie_id is not None:
        filtros.append("s.id = $serie_id")
        params["serie_id"] = serie_id
    if puntuacion_min is not None:
        filtros.append("r.puntuacion >= $puntuacion_min")
        params["puntuacion_min"] = puntuacion_min
    if puntuacion_max is not None:
        filtros.append("r.puntuacion <= $puntuacion_max")
        params["puntuacion_max"] = puntuacion_max
    if contiene_spoilers is not None:
        filtros.append("sobre.contieneSpoilers = $contiene_spoilers")
        params["contiene_spoilers"] = contiene_spoilers

    where_clause = f"WHERE {' AND '.join(filtros)}" if filtros else ""

    query_total = f"""
        MATCH (u:Usuario)-[escribio:ESCRIBIO]->(r:Resena)-[sobre:SOBRE]->(s:Serie)
        {where_clause}
        RETURN count(r) AS total
    """

    query_items = f"""
        MATCH (u:Usuario)-[escribio:ESCRIBIO]->(r:Resena)-[sobre:SOBRE]->(s:Serie)
        {where_clause}
        RETURN r, escribio, sobre, u.id AS usuario_id, s.id AS serie_id
        ORDER BY r.fecha DESC
        SKIP $skip LIMIT $limit
    """

    with get_session() as session:
        total = session.run(query_total, **params).single()["total"]
        result = session.run(query_items, **params)
        items = [_serializar_resena_completa(rec) for rec in result]

    return {"total": total, "items": items}


def crear(
    usuario_id: str,
    serie_id: str,
    texto: str,
    puntuacion: int,
    etiquetas: list[str],
    visibilidad: str,
    contieneSpoilers: bool,
    temporadaAfectada: Optional[int],
    protagonista: bool,
) -> Optional[dict]:
    """Crea Resena + ESCRIBIO + SOBRE en una sola operación atómica.

    Devuelve None si el usuario o la serie no existen.
    """
    nuevo_id = _generar_id()
    hoy = date.today().isoformat()

    query = """
        MATCH (u:Usuario {id: $usuario_id})
        MATCH (s:Serie {id: $serie_id})
        CREATE (r:Resena {
            id: $id,
            texto: $texto,
            puntuacion: $puntuacion,
            fecha: date($hoy),
            etiquetas: $etiquetas,
            util: 0
        })
        CREATE (u)-[escribio:ESCRIBIO {
            fecha: date($hoy),
            editada: false,
            visibilidad: $visibilidad
        }]->(r)
        CREATE (r)-[sobre:SOBRE {
            verificada: false,
            contieneSpoilers: $contieneSpoilers,
            temporadaAfectada: $temporadaAfectada,
            protagonista: $protagonista
        }]->(s)
        RETURN r, escribio, sobre, u.id AS usuario_id, s.id AS serie_id
    """
    with get_session() as session:
        record = session.run(
            query,
            id=nuevo_id,
            usuario_id=usuario_id,
            serie_id=serie_id,
            texto=texto,
            puntuacion=puntuacion,
            hoy=hoy,
            etiquetas=etiquetas,
            visibilidad=visibilidad,
            contieneSpoilers=contieneSpoilers,
            temporadaAfectada=temporadaAfectada,
            protagonista=protagonista,
        ).single()
        if record is None:
            return None
        return _serializar_resena_completa(record)


def actualizar(resena_id: str, propiedades: dict) -> Optional[dict]:
    """Actualiza propiedades del nodo Resena y marca ESCRIBIO.editada = true.

    Bloquea cambios sobre id y fecha (la fecha original no debe mutar).
    Devuelve la reseña actualizada o None si no existe.
    """
    props_filtradas = {
        k: v for k, v in propiedades.items() if k not in ("id", "fecha")
    }

    query = """
        MATCH (u:Usuario)-[escribio:ESCRIBIO]->(r:Resena {id: $id})-[sobre:SOBRE]->(s:Serie)
        SET r += $propiedades, escribio.editada = true
        RETURN r, escribio, sobre, u.id AS usuario_id, s.id AS serie_id
    """
    with get_session() as session:
        record = session.run(query, id=resena_id, propiedades=props_filtradas).single()
        if record is None:
            return None
        return _serializar_resena_completa(record)


def eliminar(resena_id: str) -> bool:
    """DETACH DELETE de la reseña — borra el nodo y sus relaciones ESCRIBIO/SOBRE.

    Devuelve True si existía, False si no.
    """
    query = """
        MATCH (r:Resena {id: $id})
        WITH r, count(r) AS existia
        DETACH DELETE r
        RETURN existia
    """
    with get_session() as session:
        record = session.run(query, id=resena_id).single()
        if record is None:
            return False
        return record["existia"] > 0
