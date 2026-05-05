"""Repository para relaciones de Persona 1 y Persona 2."""

from typing import Optional

from app.database import get_session
from app.repositories._helpers import to_native


# ============================================
# HELPERS PERSONA 2
# ============================================


def _filtrar_no_nulos(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


# ============================================
# PERSONA 1 — RELACIONES DE SERIE
# ============================================


def crear_pertenece_a(serie_id: str, genero_id: str, data: dict) -> Optional[dict]:
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
    with get_session() as session:
        record = session.run(query, serie_id=serie_id, genero_id=genero_id, **data).single()
        if not record:
            return None
        row = dict(record)
        return to_native(row)


def actualizar_pertenece_a(serie_id: str, genero_id: str, propiedades: dict) -> Optional[dict]:
    for k, v in propiedades.items():
        if hasattr(v, "isoformat"):
            propiedades[k] = v.isoformat()

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

    query = f"""
        MATCH (s:Serie {{id: $serie_id}})-[r:PERTENECE_A]->(g:Genero {{id: $genero_id}})
        SET {", ".join(set_parts)}
        RETURN s.id AS serie_id, g.id AS genero_id,
               r.esPrincipal AS esPrincipal,
               r.relevancia AS relevancia,
               r.fechaAsignacion AS fechaAsignacion
    """
    with get_session() as session:
        record = session.run(query, params).single()
        if not record:
            return None
        return to_native(dict(record))


def eliminar_pertenece_a(serie_id: str, genero_id: str) -> bool:
    query = """
        MATCH (s:Serie {id: $serie_id})-[r:PERTENECE_A]->(g:Genero {id: $genero_id})
        DELETE r
        RETURN count(r) AS eliminadas
    """
    with get_session() as session:
        record = session.run(query, serie_id=serie_id, genero_id=genero_id).single()
        return bool(record and record["eliminadas"] > 0)


def crear_transmite(plataforma_id: str, serie_id: str, data: dict) -> Optional[dict]:
    fecha = data.get("fechaDisponible")
    if hasattr(fecha, "isoformat"):
        data["fechaDisponible"] = fecha.isoformat()

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
    with get_session() as session:
        record = session.run(query, plataforma_id=plataforma_id, serie_id=serie_id, **data).single()
        if not record:
            return None
        return to_native(dict(record))


def crear_similar_a(serie1_id: str, serie2_id: str, data: dict) -> Optional[dict]:
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
    with get_session() as session:
        record = session.run(query, serie1_id=serie1_id, serie2_id=serie2_id, **data).single()
        if not record:
            return None
        return to_native(dict(record))


# ============================================
# PERSONA 2 — RELACIONES DE USUARIO
# ============================================


def marcar_vio(
    usuario_id: str,
    serie_id: str,
    porcentajeVisto: float,
    completada: bool,
    calificacion: Optional[float] = None,
) -> Optional[dict]:
    props = _filtrar_no_nulos(
        {
            "porcentajeVisto": porcentajeVisto,
            "completada": completada,
            "calificacion": calificacion,
        }
    )
    query = """
        MATCH (u:Usuario {id: $usuario_id})
        MATCH (s:Serie {id: $serie_id})
        MERGE (u)-[r:VIO]->(s)
        ON CREATE SET r.fecha = date()
        SET r += $props
        RETURN r
    """
    with get_session() as session:
        record = session.run(query, usuario_id=usuario_id, serie_id=serie_id, props=props).single()
        if record is None:
            return None
        return to_native(dict(record["r"]))


def actualizar_vio(
    usuario_id: str,
    serie_id: str,
    porcentajeVisto: Optional[float] = None,
    completada: Optional[bool] = None,
    calificacion: Optional[float] = None,
) -> Optional[dict]:
    """Actualiza propiedades de una relación VIO existente.

    Devuelve la relación actualizada o None si la relación no existe
    (porque no se ha marcado la serie como vista todavía).
    """
    props = _filtrar_no_nulos(
        {
            "porcentajeVisto": porcentajeVisto,
            "completada": completada,
            "calificacion": calificacion,
        }
    )
    query = """
        MATCH (u:Usuario {id: $usuario_id})-[r:VIO]->(s:Serie {id: $serie_id})
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


def eliminar_vio(usuario_id: str, serie_id: str) -> bool:
    """Elimina la relación VIO entre un usuario y una serie."""
    query = """
        MATCH (u:Usuario {id: $usuario_id})-[r:VIO]->(s:Serie {id: $serie_id})
        DELETE r
        RETURN count(r) AS eliminadas
    """
    with get_session() as session:
        record = session.run(
            query, usuario_id=usuario_id, serie_id=serie_id
        ).single()
        return bool(record and record["eliminadas"] > 0)


def actualizar_vio_masivo(usuario_id: str, items: list[dict]) -> int:
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


def dar_like(
    usuario_id: str,
    serie_id: str,
    puntuacion: Optional[int] = None,
    notificarx: Optional[bool] = None,
) -> Optional[dict]:
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
        record = session.run(query, usuario_id=usuario_id, serie_id=serie_id, props=props).single()
        if record is None:
            return None
        return to_native(dict(record["r"]))


def quitar_like(usuario_id: str, serie_id: str) -> bool:
    """Elimina la relación LE_GUSTA entre un usuario y una serie."""
    query = """
        MATCH (u:Usuario {id: $usuario_id})-[r:LE_GUSTA]->(s:Serie {id: $serie_id})
        DELETE r
        RETURN count(r) AS eliminadas
    """
    with get_session() as session:
        record = session.run(
            query, usuario_id=usuario_id, serie_id=serie_id
        ).single()
        return bool(record and record["eliminadas"] > 0)


def quitar_like_masivo(usuario_id: str, serie_ids: list[str]) -> int:
    query = """
        MATCH (u:Usuario {id: $usuario_id})-[r:LE_GUSTA]->(s:Serie)
        WHERE s.id IN $serie_ids
        WITH collect(r) AS rels
        FOREACH (r IN rels | DELETE r)
        RETURN size(rels) AS afectados
    """
    with get_session() as session:
        record = session.run(query, usuario_id=usuario_id, serie_ids=serie_ids).single()
        return record["afectados"] if record else 0


def agregar_a_lista(
    usuario_id: str,
    serie_id: str,
    prioridad: Optional[int] = None,
    notificaciones: Optional[bool] = None,
) -> Optional[dict]:
    props = _filtrar_no_nulos({"prioridad": prioridad, "notificaciones": notificaciones})
    query = """
        MATCH (u:Usuario {id: $usuario_id})
        MATCH (s:Serie {id: $serie_id})
        MERGE (u)-[r:EN_LISTA]->(s)
        ON CREATE SET r.fechaAgregado = date()
        SET r += $props
        RETURN r
    """
    with get_session() as session:
        record = session.run(query, usuario_id=usuario_id, serie_id=serie_id, props=props).single()
        if record is None:
            return None
        return to_native(dict(record["r"]))


def quitar_de_lista(usuario_id: str, serie_id: str) -> bool:
    """Elimina la relación EN_LISTA entre un usuario y una serie (quitar de watchlist)."""
    query = """
        MATCH (u:Usuario {id: $usuario_id})-[r:EN_LISTA]->(s:Serie {id: $serie_id})
        DELETE r
        RETURN count(r) AS eliminadas
    """
    with get_session() as session:
        record = session.run(
            query, usuario_id=usuario_id, serie_id=serie_id
        ).single()
        return bool(record and record["eliminadas"] > 0)


def seguir(
    usuario_id: str,
    otro_usuario_id: str,
    notificaciones: Optional[bool] = None,
) -> Optional[dict]:
    if usuario_id == otro_usuario_id:
        return None

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


def dejar_de_seguir(usuario_id: str, otro_usuario_id: str) -> bool:
    """Elimina la relación SIGUE_A entre dos usuarios.

    Si la relación inversa existe, actualiza su flag `mutuo` a false.
    """
    query = """
        MATCH (u:Usuario {id: $usuario_id})-[r:SIGUE_A]->(o:Usuario {id: $otro_id})
        WITH u, o, r
        OPTIONAL MATCH (o)-[r2:SIGUE_A]->(u)
        FOREACH (_ IN CASE WHEN r2 IS NOT NULL THEN [1] ELSE [] END |
            SET r2.mutuo = false
        )
        DELETE r
        RETURN count(r) AS eliminadas
    """
    with get_session() as session:
        record = session.run(
            query, usuario_id=usuario_id, otro_id=otro_usuario_id
        ).single()
        return bool(record and record["eliminadas"] > 0)
