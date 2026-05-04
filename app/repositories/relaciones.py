"""Repository para relaciones del Usuario.

Cypher para las relaciones:
- Usuario→Serie:   VIO, LE_GUSTA, EN_LISTA
- Usuario→Usuario: SIGUE_A

Patrón general:
- POST individual → MERGE (idempotente: si existe la actualiza)
- PATCH masivo    → UNWIND + MATCH + SET
- DELETE masivo   → MATCH + WHERE id IN [...] + DELETE
"""
from typing import Optional

from app.database import get_session
from app.repositories._helpers import to_native


def _filtrar_no_nulos(d: dict) -> dict:
    """Quita las claves con valor None — para no sobrescribir con null en Neo4j."""
    return {k: v for k, v in d.items() if v is not None}


# ============================================
# Usuario -[VIO]-> Serie
# ============================================

def marcar_vio(
    usuario_id: str,
    serie_id: str,
    porcentajeVisto: float,
    completada: bool,
    calificacion: Optional[float] = None,
) -> Optional[dict]:
    """MERGE de la relación VIO. Crea o actualiza.

    Devuelve la relación serializada, o None si el usuario o la serie no existen.
    """
    props = _filtrar_no_nulos({
        "porcentajeVisto": porcentajeVisto,
        "completada": completada,
        "calificacion": calificacion,
    })
    query = """
        MATCH (u:Usuario {id: $usuario_id})
        MATCH (s:Serie {id: $serie_id})
        MERGE (u)-[r:VIO]->(s)
        ON CREATE SET r.fecha = date()
        SET r += $props
        RETURN r
    """
    with get_session() as session:
        record = session.run(
            query, usuario_id=usuario_id, serie_id=serie_id, props=props
        ).single()
        if record is None:
            return None
        return to_native(dict(record["r"]))


def actualizar_vio_masivo(usuario_id: str, items: list[dict]) -> int:
    """Actualiza varias relaciones VIO del usuario en una sola transacción.

    Cada item debe traer `serie_id` + las propiedades a actualizar.
    Devuelve la cantidad de relaciones actualizadas.
    """
    payload = []
    for item in items:
        serie_id = item.get("serie_id")
        props = _filtrar_no_nulos({k: v for k, v in item.items() if k != "serie_id"})
        payload.append({"serie_id": serie_id, "props": props})

    query = """
        UNWIND $items AS item
        MATCH (u:Usuario {id: $usuario_id})-[r:VIO]->(s:Serie {id: item.serie_id})
        SET r += item.props
        RETURN count(r) AS afectados
    """
    with get_session() as session:
        record = session.run(query, usuario_id=usuario_id, items=payload).single()
        return record["afectados"] if record else 0


# ============================================
# Usuario -[LE_GUSTA]-> Serie
# ============================================

def dar_like(
    usuario_id: str,
    serie_id: str,
    puntuacion: Optional[int] = None,
    notificarx: Optional[bool] = None,
) -> Optional[dict]:
    """MERGE de LE_GUSTA. Crea o actualiza."""
    props = _filtrar_no_nulos({"puntuacion": puntuacion, "notificarx": notificarx})
    query = """
        MATCH (u:Usuario {id: $usuario_id})
        MATCH (s:Serie {id: $serie_id})
        MERGE (u)-[r:LE_GUSTA]->(s)
        ON CREATE SET r.fecha = date()
        SET r += $props
        RETURN r
    """
    with get_session() as session:
        record = session.run(
            query, usuario_id=usuario_id, serie_id=serie_id, props=props
        ).single()
        if record is None:
            return None
        return to_native(dict(record["r"]))


def quitar_like_masivo(usuario_id: str, serie_ids: list[str]) -> int:
    """Quita el LE_GUSTA del usuario sobre varias series. Devuelve cuántas se borraron."""
    query = """
        MATCH (u:Usuario {id: $usuario_id})-[r:LE_GUSTA]->(s:Serie)
        WHERE s.id IN $serie_ids
        WITH r, count(r) AS _
        DELETE r
        RETURN count(_) AS afectados
    """
    with get_session() as session:
        record = session.run(query, usuario_id=usuario_id, serie_ids=serie_ids).single()
        return record["afectados"] if record else 0


# ============================================
# Usuario -[EN_LISTA]-> Serie
# ============================================

def agregar_a_lista(
    usuario_id: str,
    serie_id: str,
    prioridad: Optional[int] = None,
    notificaciones: Optional[bool] = None,
) -> Optional[dict]:
    """MERGE de EN_LISTA."""
    props = _filtrar_no_nulos({
        "prioridad": prioridad,
        "notificaciones": notificaciones,
    })
    query = """
        MATCH (u:Usuario {id: $usuario_id})
        MATCH (s:Serie {id: $serie_id})
        MERGE (u)-[r:EN_LISTA]->(s)
        ON CREATE SET r.fechaAgregado = date()
        SET r += $props
        RETURN r
    """
    with get_session() as session:
        record = session.run(
            query, usuario_id=usuario_id, serie_id=serie_id, props=props
        ).single()
        if record is None:
            return None
        return to_native(dict(record["r"]))


# ============================================
# Usuario -[SIGUE_A]-> Usuario
# ============================================

def seguir(
    usuario_id: str,
    otro_usuario_id: str,
    notificaciones: Optional[bool] = None,
) -> Optional[dict]:
    """MERGE de SIGUE_A. Si el otro ya sigue de vuelta, marca mutuo=true en ambas."""
    if usuario_id == otro_usuario_id:
        return None  # un usuario no puede seguirse a sí mismo

    props = _filtrar_no_nulos({"notificaciones": notificaciones})
    query = """
        MATCH (u:Usuario {id: $usuario_id})
        MATCH (o:Usuario {id: $otro_id})
        MERGE (u)-[r:SIGUE_A]->(o)
        ON CREATE SET r.fechaSeguimiento = date()
        SET r += $props
        WITH u, o, r
        OPTIONAL MATCH (o)-[r2:SIGUE_A]->(u)
        FOREACH (_ IN CASE WHEN r2 IS NOT NULL THEN [1] ELSE [] END |
            SET r.mutuo = true, r2.mutuo = true
        )
        FOREACH (_ IN CASE WHEN r2 IS NULL THEN [1] ELSE [] END |
            SET r.mutuo = false
        )
        RETURN r
    """
    with get_session() as session:
        record = session.run(
            query, usuario_id=usuario_id, otro_id=otro_usuario_id, props=props
        ).single()
        if record is None:
            return None
        return to_native(dict(record["r"]))
