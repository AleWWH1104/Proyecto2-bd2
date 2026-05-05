"""Script para poblar Neo4j con los datos de los CSVs.

Ejecutar:
    uv run python scripts/seed.py

Lee todos los CSVs de la carpeta data/ y los inserta en Neo4j.
Crea índices para acelerar las queries.
"""
import csv
import sys
from pathlib import Path

# Permitir importar desde app/
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_session, Neo4jDriver

DATA_DIR = Path(__file__).parent.parent / "data"


def leer_csv(filename):
    """Lee un CSV y devuelve lista de diccionarios."""
    path = DATA_DIR / filename
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def to_bool(v):
    """Convierte string a bool."""
    return str(v).lower() in ("true", "1", "yes", "sí", "si")


def to_list(v):
    """Convierte 'a|b|c' a lista ['a','b','c']."""
    if not v:
        return []
    return [x.strip() for x in str(v).split("|") if x.strip()]


def crear_indices(session):
    """Crea índices para acelerar las queries."""
    print("Creando índices...")
    indices = [
        "CREATE INDEX serie_id IF NOT EXISTS FOR (n:Serie) ON (n.id)",
        "CREATE INDEX usuario_id IF NOT EXISTS FOR (n:Usuario) ON (n.id)",
        "CREATE INDEX actor_id IF NOT EXISTS FOR (n:Actor) ON (n.id)",
        "CREATE INDEX genero_id IF NOT EXISTS FOR (n:Genero) ON (n.id)",
        "CREATE INDEX plataforma_id IF NOT EXISTS FOR (n:Plataforma) ON (n.id)",
        "CREATE INDEX estudio_id IF NOT EXISTS FOR (n:EstudioProduccion) ON (n.id)",
        "CREATE INDEX resena_id IF NOT EXISTS FOR (n:Resena) ON (n.id)",
        "CREATE INDEX serie_titulo IF NOT EXISTS FOR (n:Serie) ON (n.titulo)",
    ]
    for idx in indices:
        session.run(idx)
    print("Índices creados")


def cargar_generos(session):
    rows = leer_csv("generos.csv")
    print(f"Cargando {len(rows)} géneros...")
    query = """
    UNWIND $rows AS row
    MERGE (g:Genero {id: row.id})
    SET g.nombre = row.nombre,
        g.descripcion = row.descripcion,
        g.popularidad = toFloat(row.popularidad),
        g.tendencia = row.tendencia,
        g.anio = toInteger(row.anio)
    """
    procesados = [{
        **r,
        "tendencia": to_bool(r["tendencia"]),
    } for r in rows]
    session.run(query, rows=procesados)


def cargar_plataformas(session):
    rows = leer_csv("plataformas.csv")
    print(f"Cargando {len(rows)} plataformas...")
    query = """
    UNWIND $rows AS row
    MERGE (p:Plataforma {id: row.id})
    SET p.nombre = row.nombre,
        p.pais = row.pais,
        p.precio = toFloat(row.precio),
        p.fechaFundacion = date(row.fechaFundacion),
        p.suscriptores = toInteger(row.suscriptores)
    """
    session.run(query, rows=rows)


def cargar_estudios(session):
    rows = leer_csv("estudios.csv")
    print(f"Cargando {len(rows)} estudios...")
    query = """
    UNWIND $rows AS row
    MERGE (e:EstudioProduccion {id: row.id})
    SET e.nombre = row.nombre,
        e.pais = row.pais,
        e.anioFundacion = toInteger(row.anioFundacion),
        e.activo = row.activo,
        e.presupuestoPromedio = toFloat(row.presupuestoPromedio),
        e.premios = toInteger(row.premios),
        e.generosPrincipales = row.generosPrincipales
    """
    procesados = [{
        **r,
        "activo": to_bool(r["activo"]),
        "generosPrincipales": to_list(r["generosPrincipales"]),
    } for r in rows]
    session.run(query, rows=procesados)


def cargar_actores(session):
    """Carga actores. Algunos tienen multi-label (Actor + Director)."""
    rows = leer_csv("actores.csv")
    print(f"Cargando {len(rows)} actores...")

    # Separar entre actores normales y actor-directores
    solo_actor = [r for r in rows if "Director" not in r["labels"]]
    actor_director = [r for r in rows if "Director" in r["labels"]]

    # Cargar los que solo son Actor
    query_actor = """
    UNWIND $rows AS row
    MERGE (a:Actor {id: row.id})
    SET a.nombre = row.nombre,
        a.nacionalidad = row.nacionalidad,
        a.fechaNacimiento = date(row.fechaNacimiento),
        a.premios = toInteger(row.premios),
        a.activo = row.activo,
        a.popularidad = toFloat(row.popularidad),
        a.papeles = row.papeles
    """
    procesados_actor = [{
        **r,
        "activo": to_bool(r["activo"]),
        "papeles": to_list(r["papeles"]),
    } for r in solo_actor]
    session.run(query_actor, rows=procesados_actor)

    # Cargar los que son Actor:Director (multi-label)
    query_director = """
    UNWIND $rows AS row
    MERGE (a:Actor:Director {id: row.id})
    SET a.nombre = row.nombre,
        a.nacionalidad = row.nacionalidad,
        a.fechaNacimiento = date(row.fechaNacimiento),
        a.premios = toInteger(row.premios),
        a.activo = row.activo,
        a.popularidad = toFloat(row.popularidad),
        a.papeles = row.papeles
    """
    procesados_dir = [{
        **r,
        "activo": to_bool(r["activo"]),
        "papeles": to_list(r["papeles"]),
    } for r in actor_director]
    session.run(query_director, rows=procesados_dir)
    print(f"  -> {len(actor_director)} con multi-label (Actor:Director)")


def cargar_series(session):
    rows = leer_csv("series.csv")
    print(f"Cargando {len(rows)} series...")
    query = """
    UNWIND $rows AS row
    MERGE (s:Serie {id: row.id})
    SET s.titulo = row.titulo,
        s.sinopsis = row.sinopsis,
        s.anio = toInteger(row.anio),
        s.calificacion = toFloat(row.calificacion),
        s.numTemporadas = toInteger(row.numTemporadas),
        s.numEpisodios = toInteger(row.numEpisodios),
        s.estadoEmision = row.estadoEmision,
        s.activa = row.activa
    """
    procesados = [{
        **r,
        "estadoEmision": to_bool(r["estadoEmision"]),
        "activa": to_bool(r["activa"]),
    } for r in rows]
    session.run(query, rows=procesados)


def cargar_usuarios(session):
    rows = leer_csv("usuarios.csv")
    print(f"Cargando {len(rows)} usuarios...")
    query = """
    UNWIND $rows AS row
    MERGE (u:Usuario {id: row.id})
    SET u.nombre = row.nombre,
        u.email = row.email,
        u.edad = toInteger(row.edad),
        u.fechaRegistro = date(row.fechaRegistro),
        u.activo = row.activo
    """
    procesados = [{
        **r,
        "activo": to_bool(r["activo"]),
    } for r in rows]
    session.run(query, rows=procesados)


def cargar_resenas(session):
    rows = leer_csv("resenas.csv")
    print(f"Cargando {len(rows)} reseñas...")
    query = """
    UNWIND $rows AS row
    MERGE (r:Resena {id: row.id})
    SET r.texto = row.texto,
        r.puntuacion = toInteger(row.puntuacion),
        r.fecha = date(row.fecha),
        r.etiquetas = row.etiquetas,
        r.util = toInteger(row.util)
    """
    procesados = [{
        **r,
        "etiquetas": to_list(r["etiquetas"]),
    } for r in rows]
    session.run(query, rows=procesados)


# ============================================
# RELACIONES
# ============================================

def cargar_pertenece_a(session):
    rows = leer_csv("rel_pertenece_a.csv")
    print(f"Cargando {len(rows)} relaciones PERTENECE_A...")
    query = """
    UNWIND $rows AS row
    MATCH (s:Serie {id: row.serie_id})
    MATCH (g:Genero {id: row.genero_id})
    MERGE (s)-[r:PERTENECE_A]->(g)
    SET r.esPrincipal = row.esPrincipal,
        r.relevancia = toFloat(row.relevancia),
        r.fechaAsignacion = date(row.fechaAsignacion)
    """
    procesados = [{**r, "esPrincipal": to_bool(r["esPrincipal"])} for r in rows]
    session.run(query, rows=procesados)


def cargar_transmite(session):
    rows = leer_csv("rel_transmite.csv")
    print(f"Cargando {len(rows)} relaciones TRANSMITE...")
    query = """
    UNWIND $rows AS row
    MATCH (p:Plataforma {id: row.plataforma_id})
    MATCH (s:Serie {id: row.serie_id})
    MERGE (p)-[r:TRANSMITE]->(s)
    SET r.fechaDisponible = date(row.fechaDisponible),
        r.exclusiva = row.exclusiva,
        r.regiones = row.regiones
    """
    procesados = [{
        **r,
        "exclusiva": to_bool(r["exclusiva"]),
        "regiones": to_list(r["regiones"]),
    } for r in rows]
    session.run(query, rows=procesados)


def cargar_produjo(session):
    rows = leer_csv("rel_produjo.csv")
    print(f"Cargando {len(rows)} relaciones PRODUJO...")
    query = """
    UNWIND $rows AS row
    MATCH (e:EstudioProduccion {id: row.estudio_id})
    MATCH (s:Serie {id: row.serie_id})
    MERGE (e)-[r:PRODUJO]->(s)
    SET r.anio = toInteger(row.anio),
        r.presupuesto = toFloat(row.presupuesto),
        r.distribucion = row.distribucion
    """
    session.run(query, rows=rows)


def cargar_actua_en(session):
    rows = leer_csv("rel_actua_en.csv")
    print(f"Cargando {len(rows)} relaciones ACTUA_EN...")
    query = """
    UNWIND $rows AS row
    MATCH (a:Actor {id: row.actor_id})
    MATCH (s:Serie {id: row.serie_id})
    MERGE (a)-[r:ACTUA_EN]->(s)
    SET r.personaje = row.personaje,
        r.protagonista = row.protagonista,
        r.temporadas = row.temporadas
    """
    procesados = [{
        **r,
        "protagonista": to_bool(r["protagonista"]),
        "temporadas": [int(t) for t in to_list(r["temporadas"])],
    } for r in rows]
    session.run(query, rows=procesados)


def cargar_dirige(session):
    rows = leer_csv("rel_dirige.csv")
    print(f"Cargando {len(rows)} relaciones DIRIGE...")
    query = """
    UNWIND $rows AS row
    MATCH (a:Director {id: row.actor_id})
    MATCH (s:Serie {id: row.serie_id})
    MERGE (a)-[r:DIRIGE]->(s)
    SET r.temporadas = row.temporadas,
        r.anioInicio = toInteger(row.anioInicio),
        r.esPrincipal = row.esPrincipal
    """
    procesados = [{
        **r,
        "esPrincipal": to_bool(r["esPrincipal"]),
        "temporadas": [int(t) for t in to_list(r["temporadas"])],
    } for r in rows]
    session.run(query, rows=procesados)


def cargar_similar_a(session):
    rows = leer_csv("rel_similar_a.csv")
    print(f"Cargando {len(rows)} relaciones SIMILAR_A...")
    query = """
    UNWIND $rows AS row
    MATCH (s1:Serie {id: row.serie1_id})
    MATCH (s2:Serie {id: row.serie2_id})
    MERGE (s1)-[r:SIMILAR_A]->(s2)
    SET r.puntuacionSimilitud = toFloat(row.puntuacionSimilitud),
        r.algoritmo = row.algoritmo,
        r.fechaCalculada = date(row.fechaCalculada)
    """
    session.run(query, rows=rows)


def cargar_vio(session):
    rows = leer_csv("rel_vio.csv")
    print(f"Cargando {len(rows)} relaciones VIO...")
    query = """
    UNWIND $rows AS row
    MATCH (u:Usuario {id: row.usuario_id})
    MATCH (s:Serie {id: row.serie_id})
    MERGE (u)-[r:VIO]->(s)
    SET r.fecha = date(row.fecha),
        r.porcentajeVisto = toFloat(row.porcentajeVisto),
        r.completada = row.completada
    """
    procesados = [{**r, "completada": to_bool(r["completada"])} for r in rows]
    session.run(query, rows=procesados)


def cargar_le_gusta(session):
    rows = leer_csv("rel_le_gusta.csv")
    print(f"Cargando {len(rows)} relaciones LE_GUSTA...")
    query = """
    UNWIND $rows AS row
    MATCH (u:Usuario {id: row.usuario_id})
    MATCH (s:Serie {id: row.serie_id})
    MERGE (u)-[r:LE_GUSTA]->(s)
    SET r.fecha = date(row.fecha),
        r.puntuacion = toFloat(row.puntuacion),
        r.notificado = row.notificado
    """
    procesados = [{**r, "notificado": to_bool(r["notificado"])} for r in rows]
    session.run(query, rows=procesados)


def cargar_en_lista(session):
    rows = leer_csv("rel_en_lista.csv")
    print(f"Cargando {len(rows)} relaciones EN_LISTA...")
    query = """
    UNWIND $rows AS row
    MATCH (u:Usuario {id: row.usuario_id})
    MATCH (s:Serie {id: row.serie_id})
    MERGE (u)-[r:EN_LISTA]->(s)
    SET r.fechaAgregado = date(row.fechaAgregado),
        r.prioridad = toInteger(row.prioridad),
        r.notificaciones = row.notificaciones
    """
    procesados = [{**r, "notificaciones": to_bool(r["notificaciones"])} for r in rows]
    session.run(query, rows=procesados)


def cargar_sigue_a(session):
    rows = leer_csv("rel_sigue_a.csv")
    print(f"Cargando {len(rows)} relaciones SIGUE_A...")
    query = """
    UNWIND $rows AS row
    MATCH (u1:Usuario {id: row.usuario1_id})
    MATCH (u2:Usuario {id: row.usuario2_id})
    MERGE (u1)-[r:SIGUE_A]->(u2)
    SET r.fechaSeguimiento = date(row.fechaSeguimiento),
        r.mutuo = row.mutuo,
        r.notificaciones = row.notificaciones
    """
    procesados = [{
        **r,
        "mutuo": to_bool(r["mutuo"]),
        "notificaciones": to_bool(r["notificaciones"]),
    } for r in rows]
    session.run(query, rows=procesados)


def cargar_escribio(session):
    rows = leer_csv("rel_escribio.csv")
    print(f"Cargando {len(rows)} relaciones ESCRIBIO...")
    query = """
    UNWIND $rows AS row
    MATCH (u:Usuario {id: row.usuario_id})
    MATCH (r:Resena {id: row.resena_id})
    MERGE (u)-[rel:ESCRIBIO]->(r)
    SET rel.fecha = date(row.fecha),
        rel.editada = row.editada,
        rel.visibilidad = row.visibilidad
    """
    procesados = [{**r, "editada": to_bool(r["editada"])} for r in rows]
    session.run(query, rows=procesados)


def cargar_sobre(session):
    rows = leer_csv("rel_sobre.csv")
    print(f"Cargando {len(rows)} relaciones SOBRE...")
    query = """
    UNWIND $rows AS row
    MATCH (r:Resena {id: row.resena_id})
    MATCH (s:Serie {id: row.serie_id})
    MERGE (r)-[rel:SOBRE]->(s)
    SET rel.verificada = row.verificada,
        rel.temporadaResenada = toInteger(row.temporadaResenada),
        rel.contieneSpoilers = row.contieneSpoilers
    """
    procesados = [{
        **r,
        "verificada": to_bool(r["verificada"]),
        "contieneSpoilers": to_bool(r["contieneSpoilers"]),
    } for r in rows]
    session.run(query, rows=procesados)


# ============================================
# MAIN
# ============================================

def cargar_todo(session) -> dict:
    """Ejecuta toda la carga de CSVs en orden y devuelve los conteos finales.

    Reusable desde el script CLI y desde el endpoint POST /admin/cargar-csv.
    """
    crear_indices(session)
    cargar_generos(session)
    cargar_plataformas(session)
    cargar_estudios(session)
    cargar_actores(session)
    cargar_series(session)
    cargar_usuarios(session)
    cargar_resenas(session)
    cargar_pertenece_a(session)
    cargar_transmite(session)
    cargar_produjo(session)
    cargar_actua_en(session)
    cargar_dirige(session)
    cargar_similar_a(session)
    cargar_vio(session)
    cargar_le_gusta(session)
    cargar_en_lista(session)
    cargar_sigue_a(session)
    cargar_escribio(session)
    cargar_sobre(session)

    total_nodos = session.run("MATCH (n) RETURN count(n) AS total").single()["total"]
    total_rels = session.run("MATCH ()-[r]->() RETURN count(r) AS total").single()["total"]
    return {"total_nodos": total_nodos, "total_relaciones": total_rels}


TIPOS_VALIDOS = [
    "series", "actores", "usuarios", "generos", "plataformas", "estudios", "resenas",
    "pertenece_a", "transmite", "actua_en", "vio", "le_gusta", "en_lista", "sigue_a",
    "dirige", "similar_a", "escribio", "sobre", "produjo",
]


def procesar_csv(session, tipo: str, rows: list) -> int:
    """Inserta/actualiza filas de un CSV subido según el tipo de entidad o relación."""
    if not rows:
        return 0

    if tipo == "series":
        procesados = [{**r, "estadoEmision": to_bool(r.get("estadoEmision", "")), "activa": to_bool(r.get("activa", ""))} for r in rows]
        session.run("""
            UNWIND $rows AS row
            MERGE (s:Serie {id: row.id})
            SET s.titulo = row.titulo, s.sinopsis = row.sinopsis,
                s.anio = toInteger(row.anio), s.calificacion = toFloat(row.calificacion),
                s.numTemporadas = toInteger(row.numTemporadas), s.numEpisodios = toInteger(row.numEpisodios),
                s.estadoEmision = row.estadoEmision, s.activa = row.activa
        """, rows=procesados)

    elif tipo == "actores":
        solo_actor = [r for r in rows if "Director" not in r.get("labels", "")]
        actor_director = [r for r in rows if "Director" in r.get("labels", "")]
        if solo_actor:
            p = [{**r, "activo": to_bool(r.get("activo", "")), "papeles": to_list(r.get("papeles", ""))} for r in solo_actor]
            session.run("""
                UNWIND $rows AS row
                MERGE (a:Actor {id: row.id})
                SET a.nombre = row.nombre, a.nacionalidad = row.nacionalidad,
                    a.fechaNacimiento = date(row.fechaNacimiento),
                    a.premios = toInteger(row.premios), a.activo = row.activo,
                    a.popularidad = toFloat(row.popularidad), a.papeles = row.papeles
            """, rows=p)
        if actor_director:
            p = [{**r, "activo": to_bool(r.get("activo", "")), "papeles": to_list(r.get("papeles", ""))} for r in actor_director]
            session.run("""
                UNWIND $rows AS row
                MERGE (a:Actor:Director {id: row.id})
                SET a.nombre = row.nombre, a.nacionalidad = row.nacionalidad,
                    a.fechaNacimiento = date(row.fechaNacimiento),
                    a.premios = toInteger(row.premios), a.activo = row.activo,
                    a.popularidad = toFloat(row.popularidad), a.papeles = row.papeles
            """, rows=p)

    elif tipo == "usuarios":
        procesados = [{**r, "activo": to_bool(r.get("activo", ""))} for r in rows]
        session.run("""
            UNWIND $rows AS row
            MERGE (u:Usuario {id: row.id})
            SET u.nombre = row.nombre, u.email = row.email,
                u.edad = toInteger(row.edad), u.fechaRegistro = date(row.fechaRegistro),
                u.activo = row.activo
        """, rows=procesados)

    elif tipo == "generos":
        procesados = [{**r, "tendencia": to_bool(r.get("tendencia", ""))} for r in rows]
        session.run("""
            UNWIND $rows AS row
            MERGE (g:Genero {id: row.id})
            SET g.nombre = row.nombre, g.descripcion = row.descripcion,
                g.popularidad = toFloat(row.popularidad), g.tendencia = row.tendencia,
                g.anio = toInteger(row.anio)
        """, rows=procesados)

    elif tipo == "plataformas":
        session.run("""
            UNWIND $rows AS row
            MERGE (p:Plataforma {id: row.id})
            SET p.nombre = row.nombre, p.pais = row.pais,
                p.precio = toFloat(row.precio), p.fechaFundacion = date(row.fechaFundacion),
                p.suscriptores = toInteger(row.suscriptores)
        """, rows=rows)

    elif tipo == "estudios":
        procesados = [{**r, "activo": to_bool(r.get("activo", "")), "generosPrincipales": to_list(r.get("generosPrincipales", ""))} for r in rows]
        session.run("""
            UNWIND $rows AS row
            MERGE (e:EstudioProduccion {id: row.id})
            SET e.nombre = row.nombre, e.pais = row.pais,
                e.anioFundacion = toInteger(row.anioFundacion), e.activo = row.activo,
                e.presupuestoPromedio = toFloat(row.presupuestoPromedio),
                e.premios = toInteger(row.premios), e.generosPrincipales = row.generosPrincipales
        """, rows=procesados)

    elif tipo == "resenas":
        procesados = [{**r, "etiquetas": to_list(r.get("etiquetas", ""))} for r in rows]
        session.run("""
            UNWIND $rows AS row
            MERGE (r:Resena {id: row.id})
            SET r.texto = row.texto, r.puntuacion = toInteger(row.puntuacion),
                r.fecha = date(row.fecha), r.etiquetas = row.etiquetas,
                r.util = toInteger(row.util)
        """, rows=procesados)

    elif tipo == "pertenece_a":
        procesados = [{**r, "esPrincipal": to_bool(r.get("esPrincipal", ""))} for r in rows]
        session.run("""
            UNWIND $rows AS row
            MATCH (s:Serie {id: row.serie_id}), (g:Genero {id: row.genero_id})
            MERGE (s)-[r:PERTENECE_A]->(g)
            SET r.esPrincipal = row.esPrincipal, r.relevancia = toFloat(row.relevancia),
                r.fechaAsignacion = date(row.fechaAsignacion)
        """, rows=procesados)

    elif tipo == "transmite":
        procesados = [{**r, "exclusiva": to_bool(r.get("exclusiva", "")), "regiones": to_list(r.get("regiones", ""))} for r in rows]
        session.run("""
            UNWIND $rows AS row
            MATCH (p:Plataforma {id: row.plataforma_id}), (s:Serie {id: row.serie_id})
            MERGE (p)-[r:TRANSMITE]->(s)
            SET r.fechaDisponible = date(row.fechaDisponible), r.exclusiva = row.exclusiva,
                r.regiones = row.regiones
        """, rows=procesados)

    elif tipo == "actua_en":
        procesados = [{**r, "protagonista": to_bool(r.get("protagonista", "")), "temporadas": [int(t) for t in to_list(r.get("temporadas", ""))]} for r in rows]
        session.run("""
            UNWIND $rows AS row
            MATCH (a:Actor {id: row.actor_id}), (s:Serie {id: row.serie_id})
            MERGE (a)-[r:ACTUA_EN]->(s)
            SET r.personaje = row.personaje, r.protagonista = row.protagonista,
                r.temporadas = row.temporadas
        """, rows=procesados)

    elif tipo == "dirige":
        procesados = [{**r, "esPrincipal": to_bool(r.get("esPrincipal", "")), "temporadas": [int(t) for t in to_list(r.get("temporadas", ""))]} for r in rows]
        session.run("""
            UNWIND $rows AS row
            MATCH (a:Director {id: row.actor_id}), (s:Serie {id: row.serie_id})
            MERGE (a)-[r:DIRIGE]->(s)
            SET r.temporadas = row.temporadas, r.anioInicio = toInteger(row.anioInicio),
                r.esPrincipal = row.esPrincipal
        """, rows=procesados)

    elif tipo == "vio":
        procesados = [{**r, "completada": to_bool(r.get("completada", ""))} for r in rows]
        session.run("""
            UNWIND $rows AS row
            MATCH (u:Usuario {id: row.usuario_id}), (s:Serie {id: row.serie_id})
            MERGE (u)-[r:VIO]->(s)
            SET r.fecha = date(row.fecha), r.porcentajeVisto = toFloat(row.porcentajeVisto),
                r.completada = row.completada
        """, rows=procesados)

    elif tipo == "le_gusta":
        procesados = [{**r, "notificado": to_bool(r.get("notificado", ""))} for r in rows]
        session.run("""
            UNWIND $rows AS row
            MATCH (u:Usuario {id: row.usuario_id}), (s:Serie {id: row.serie_id})
            MERGE (u)-[r:LE_GUSTA]->(s)
            SET r.fecha = date(row.fecha), r.puntuacion = toFloat(row.puntuacion),
                r.notificado = row.notificado
        """, rows=procesados)

    elif tipo == "en_lista":
        procesados = [{**r, "notificaciones": to_bool(r.get("notificaciones", ""))} for r in rows]
        session.run("""
            UNWIND $rows AS row
            MATCH (u:Usuario {id: row.usuario_id}), (s:Serie {id: row.serie_id})
            MERGE (u)-[r:EN_LISTA]->(s)
            SET r.fechaAgregado = date(row.fechaAgregado), r.prioridad = toInteger(row.prioridad),
                r.notificaciones = row.notificaciones
        """, rows=procesados)

    elif tipo == "sigue_a":
        procesados = [{**r, "mutuo": to_bool(r.get("mutuo", "")), "notificaciones": to_bool(r.get("notificaciones", ""))} for r in rows]
        session.run("""
            UNWIND $rows AS row
            MATCH (u1:Usuario {id: row.usuario1_id}), (u2:Usuario {id: row.usuario2_id})
            MERGE (u1)-[r:SIGUE_A]->(u2)
            SET r.fechaSeguimiento = date(row.fechaSeguimiento), r.mutuo = row.mutuo,
                r.notificaciones = row.notificaciones
        """, rows=procesados)

    elif tipo == "similar_a":
        session.run("""
            UNWIND $rows AS row
            MATCH (s1:Serie {id: row.serie1_id}), (s2:Serie {id: row.serie2_id})
            MERGE (s1)-[r:SIMILAR_A]->(s2)
            SET r.puntuacionSimilitud = toFloat(row.puntuacionSimilitud),
                r.algoritmo = row.algoritmo, r.fechaCalculada = date(row.fechaCalculada)
        """, rows=rows)

    elif tipo == "escribio":
        procesados = [{**r, "editada": to_bool(r.get("editada", ""))} for r in rows]
        session.run("""
            UNWIND $rows AS row
            MATCH (u:Usuario {id: row.usuario_id}), (r:Resena {id: row.resena_id})
            MERGE (u)-[rel:ESCRIBIO]->(r)
            SET rel.fecha = date(row.fecha), rel.editada = row.editada,
                rel.visibilidad = row.visibilidad
        """, rows=procesados)

    elif tipo == "sobre":
        procesados = [{**r, "verificada": to_bool(r.get("verificada", "")), "contieneSpoilers": to_bool(r.get("contieneSpoilers", ""))} for r in rows]
        session.run("""
            UNWIND $rows AS row
            MATCH (r:Resena {id: row.resena_id}), (s:Serie {id: row.serie_id})
            MERGE (r)-[rel:SOBRE]->(s)
            SET rel.verificada = row.verificada, rel.temporadaResenada = toInteger(row.temporadaResenada),
                rel.contieneSpoilers = row.contieneSpoilers
        """, rows=procesados)

    elif tipo == "produjo":
        session.run("""
            UNWIND $rows AS row
            MATCH (e:EstudioProduccion {id: row.estudio_id}), (s:Serie {id: row.serie_id})
            MERGE (e)-[r:PRODUJO]->(s)
            SET r.anio = toInteger(row.anio), r.presupuesto = toFloat(row.presupuesto),
                r.distribucion = row.distribucion
        """, rows=rows)

    else:
        raise ValueError(f"Tipo desconocido: '{tipo}'. Válidos: {', '.join(TIPOS_VALIDOS)}")

    return len(rows)


def main():
    print("=" * 60)
    print("POBLANDO BASE DE DATOS")
    print("=" * 60)

    if not Neo4jDriver.verify_connectivity():
        print("ERROR: no se puede conectar a Neo4j. Verifica tu .env")
        sys.exit(1)

    with get_session() as session:
        resumen = cargar_todo(session)
        print()
        print("--- RESUMEN ---")
        print(f"Total nodos: {resumen['total_nodos']}")
        print(f"Total relaciones: {resumen['total_relaciones']}")

    Neo4jDriver.close()
    print()
    print("Listo. Base de datos poblada correctamente.")


if __name__ == "__main__":
    main()
