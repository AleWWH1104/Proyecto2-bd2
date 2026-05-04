"""Repository para usuarios.

Queries Cypher para la entidad Usuario. Cada función abre una sesión,
ejecuta el Cypher con parámetros, y devuelve dict/lista de dicts.

NUNCA concatenar strings en las queries: usar siempre parámetros ($var).
"""
import uuid
from datetime import date
from typing import Optional

from app.database import get_session
from app.repositories._helpers import to_native


def _generar_id() -> str:
    """Genera un id único para usuario tipo usr_xxxxxxxx."""
    return f"usr_{uuid.uuid4().hex[:8]}"


def _serializar_usuario(nodo) -> dict:
    """Convierte un nodo Neo4j Usuario a dict listo para Pydantic."""
    return to_native(dict(nodo))


def listar(
    edad_min: Optional[int] = None,
    edad_max: Optional[int] = None,
    activo: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
) -> dict:
    """Lista usuarios con filtros opcionales y paginación.

    Devuelve: {"total": int, "items": [usuario_dict, ...]}
    """
    # Construir filtros dinámicamente
    filtros = []
    params = {"skip": skip, "limit": limit}

    if edad_min is not None:
        filtros.append("u.edad >= $edad_min")
        params["edad_min"] = edad_min
    if edad_max is not None:
        filtros.append("u.edad <= $edad_max")
        params["edad_max"] = edad_max
    if activo is not None:
        filtros.append("u.activo = $activo")
        params["activo"] = activo

    where_clause = f"WHERE {' AND '.join(filtros)}" if filtros else ""

    query_total = f"""
        MATCH (u:Usuario)
        {where_clause}
        RETURN count(u) AS total
    """

    query_items = f"""
        MATCH (u:Usuario)
        {where_clause}
        RETURN u
        ORDER BY u.fechaRegistro DESC
        SKIP $skip LIMIT $limit
    """

    with get_session() as session:
        total = session.run(query_total, **params).single()["total"]
        result = session.run(query_items, **params)
        items = [_serializar_usuario(record["u"]) for record in result]

    return {"total": total, "items": items}


def obtener_por_id(usuario_id: str) -> Optional[dict]:
    """Obtiene un usuario por su id. Devuelve None si no existe."""
    query = """
        MATCH (u:Usuario {id: $id})
        RETURN u
    """
    with get_session() as session:
        record = session.run(query, id=usuario_id).single()
        if record is None:
            return None
        return _serializar_usuario(record["u"])


def obtener_perfil_completo(usuario_id: str) -> Optional[dict]:
    """Obtiene un usuario con todas sus relaciones (vistas, likes, lista, sigue)."""
    query = """
        MATCH (u:Usuario {id: $id})
        OPTIONAL MATCH (u)-[v:VIO]->(sv:Serie)
        OPTIONAL MATCH (u)-[lg:LE_GUSTA]->(sg:Serie)
        OPTIONAL MATCH (u)-[el:EN_LISTA]->(sl:Serie)
        OPTIONAL MATCH (u)-[sa:SIGUE_A]->(uo:Usuario)
        RETURN u,
               collect(DISTINCT {
                   serie_id: sv.id, titulo: sv.titulo,
                   fecha: v.fecha, porcentajeVisto: v.porcentajeVisto,
                   completada: v.completada
               }) AS vistas,
               collect(DISTINCT {
                   serie_id: sg.id, titulo: sg.titulo,
                   fecha: lg.fecha, puntuacion: lg.puntuacion
               }) AS gustadas,
               collect(DISTINCT {
                   serie_id: sl.id, titulo: sl.titulo,
                   fechaAgregado: el.fechaAgregado, prioridad: el.prioridad
               }) AS lista,
               collect(DISTINCT {
                   usuario_id: uo.id, nombre: uo.nombre,
                   fechaSeguimiento: sa.fechaSeguimiento, mutuo: sa.mutuo
               }) AS seguidos
    """
    with get_session() as session:
        record = session.run(query, id=usuario_id).single()
        if record is None:
            return None

        # Filtrar elementos vacíos (cuando OPTIONAL MATCH no encuentra nada)
        # y convertir cualquier neo4j.time.Date dentro de las relaciones
        vistas = [to_native(v) for v in record["vistas"] if v["serie_id"] is not None]
        gustadas = [to_native(g) for g in record["gustadas"] if g["serie_id"] is not None]
        lista = [to_native(l) for l in record["lista"] if l["serie_id"] is not None]
        seguidos = [to_native(s) for s in record["seguidos"] if s["usuario_id"] is not None]

        return {
            "usuario": _serializar_usuario(record["u"]),
            "series_vistas": vistas,
            "series_que_le_gustan": gustadas,
            "series_en_lista": lista,
            "usuarios_que_sigue": seguidos,
        }


def crear(nombre: str, email: str, edad: int, activo: bool = True) -> dict:
    """Crea un usuario nuevo y devuelve sus datos."""
    nuevo_id = _generar_id()
    fecha_registro = date.today().isoformat()

    query = """
        CREATE (u:Usuario {
            id: $id,
            nombre: $nombre,
            email: $email,
            edad: $edad,
            fechaRegistro: date($fecha_registro),
            activo: $activo
        })
        RETURN u
    """
    with get_session() as session:
        record = session.run(
            query,
            id=nuevo_id,
            nombre=nombre,
            email=email,
            edad=edad,
            fecha_registro=fecha_registro,
            activo=activo,
        ).single()
        return _serializar_usuario(record["u"])


def eliminar(usuario_id: str) -> bool:
    """Elimina un usuario y todas sus relaciones (DETACH DELETE).

    Devuelve True si se eliminó, False si no existía.
    """
    query = """
        MATCH (u:Usuario {id: $id})
        WITH u, count(u) AS existia
        DETACH DELETE u
        RETURN existia
    """
    with get_session() as session:
        record = session.run(query, id=usuario_id).single()
        if record is None:
            return False
        return record["existia"] > 0
