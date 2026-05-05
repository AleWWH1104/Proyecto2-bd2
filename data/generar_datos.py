"""
Generador de datos sintéticos para el motor de recomendación de series.

Genera ~6000 nodos coherentes y conectados:
- 50 Géneros
- 30 Plataformas
- 40 EstudioProduccion
- 800 Actores (con ~150 que también son Directores)
- 3000 Series
- 800 Usuarios
- 1500 Reseñas

Y todas las relaciones necesarias para que el grafo sea conexo.
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)  # Reproducibilidad

OUT_DIR = Path(__file__).parent

# ============================================
# DATA SEED REALISTA
# ============================================

GENEROS_BASE = [
    ("Drama", "Series con narrativa profunda y desarrollo de personajes"),
    ("Comedia", "Series para entretener y hacer reír"),
    ("Acción", "Series con secuencias intensas y aventura"),
    ("Ciencia Ficción", "Series futuristas y especulativas"),
    ("Fantasía", "Mundos mágicos y elementos sobrenaturales"),
    ("Terror", "Series de suspenso y miedo"),
    ("Misterio", "Tramas con enigmas por resolver"),
    ("Crimen", "Investigaciones criminales y thrillers"),
    ("Romance", "Historias de amor y relaciones"),
    ("Aventura", "Viajes y exploración"),
    ("Animación", "Series animadas para todas las edades"),
    ("Documental", "Contenido factual y educativo"),
    ("Histórico", "Ambientadas en períodos históricos"),
    ("Guerra", "Conflictos bélicos y militares"),
    ("Western", "El viejo oeste americano"),
    ("Musical", "Series con números musicales"),
    ("Deportes", "Competencias y narrativas deportivas"),
    ("Biográfico", "Vidas de personas reales"),
    ("Político", "Tramas con poder y gobierno"),
    ("Sobrenatural", "Elementos paranormales"),
    ("Adolescente", "Dirigidas a público joven"),
    ("Familiar", "Para toda la familia"),
    ("Médico", "Ambientes hospitalarios"),
    ("Legal", "Cortes y abogados"),
    ("Espionaje", "Agentes secretos y conspiraciones"),
    ("Distopía", "Sociedades opresivas del futuro"),
    ("Postapocalíptico", "Después del fin del mundo"),
    ("Superhéroes", "Personajes con poderes extraordinarios"),
    ("Cyberpunk", "Tecnología y sociedad oscura"),
    ("Steampunk", "Estética victoriana con tecnología vapor"),
    ("Slice of Life", "Vida cotidiana"),
    ("Psicológico", "Exploración de la mente humana"),
    ("Antología", "Historias independientes por temporada"),
    ("Procedimental", "Caso por episodio"),
    ("Sitcom", "Comedia de situaciones"),
    ("Dramedia", "Mezcla de drama y comedia"),
    ("Thriller", "Suspenso intenso"),
    ("Reality", "Contenido no ficcional"),
    ("Talk Show", "Programas de entrevistas"),
    ("Variedades", "Mezcla de formatos"),
    ("Educativo", "Aprendizaje y conocimiento"),
    ("Infantil", "Para niños"),
    ("Juvenil", "Para adolescentes"),
    ("Adulto", "Contenido para adultos"),
    ("Internacional", "Producciones de varios países"),
    ("Independiente", "Producción independiente"),
    ("Experimental", "Formato innovador"),
    ("Noir", "Estilo oscuro y cínico"),
    ("Neo-Noir", "Versión moderna del noir"),
    ("Mockumentary", "Falso documental"),
]

PLATAFORMAS_BASE = [
    ("Netflix", "Estados Unidos", 15.99, "1997-08-29", 230000000),
    ("HBO Max", "Estados Unidos", 14.99, "2020-05-27", 95000000),
    ("Disney+", "Estados Unidos", 10.99, "2019-11-12", 150000000),
    ("Amazon Prime Video", "Estados Unidos", 8.99, "2006-09-07", 200000000),
    ("Apple TV+", "Estados Unidos", 9.99, "2019-11-01", 50000000),
    ("Hulu", "Estados Unidos", 7.99, "2007-10-29", 48000000),
    ("Paramount+", "Estados Unidos", 9.99, "2014-10-28", 67000000),
    ("Peacock", "Estados Unidos", 5.99, "2020-07-15", 28000000),
    ("Crunchyroll", "Estados Unidos", 7.99, "2006-05-14", 12000000),
    ("Movistar Plus+", "España", 11.00, "2015-07-08", 4500000),
    ("Star+", "Estados Unidos", 7.99, "2021-08-31", 18000000),
    ("Discovery+", "Estados Unidos", 6.99, "2021-01-04", 24000000),
    ("Showtime", "Estados Unidos", 10.99, "1976-07-01", 27000000),
    ("Starz", "Estados Unidos", 8.99, "1994-02-01", 13000000),
    ("Vix", "México", 6.99, "2022-07-21", 6000000),
    ("Pluto TV", "Estados Unidos", 0.0, "2014-03-31", 80000000),
    ("Tubi", "Estados Unidos", 0.0, "2014-04-01", 64000000),
    ("Kocowa", "Corea del Sur", 6.99, "2017-04-13", 1500000),
    ("Viki", "Singapur", 5.99, "2007-12-01", 4500000),
    ("MUBI", "Reino Unido", 11.99, "2007-04-09", 13000000),
    ("BritBox", "Reino Unido", 8.99, "2017-03-07", 4500000),
    ("Acorn TV", "Estados Unidos", 6.99, "2011-07-26", 2000000),
    ("Curiosity Stream", "Estados Unidos", 4.99, "2015-03-18", 26000000),
    ("Shudder", "Estados Unidos", 5.99, "2015-06-01", 1500000),
    ("Crave", "Canadá", 9.99, "2014-12-11", 3000000),
    ("Stan", "Australia", 10.00, "2015-01-26", 2700000),
    ("Now TV", "Reino Unido", 9.99, "2012-07-17", 2500000),
    ("Globoplay", "Brasil", 5.50, "2015-11-02", 28000000),
    ("Claro Video", "México", 4.99, "2014-11-01", 8500000),
    ("Blim TV", "México", 3.99, "2016-02-29", 1200000),
]

ESTUDIOS_BASE = [
    "HBO", "Netflix Studios", "Disney Television", "Warner Bros TV",
    "Universal Television", "20th Century Studios", "Sony Pictures TV",
    "Paramount Television", "Lionsgate Television", "MGM Television",
    "BBC Studios", "ITV Studios", "Channel 4", "FX Productions",
    "AMC Studios", "Showtime Networks", "Bad Robot Productions",
    "Bad Wolf", "A24", "Bron Studios", "Skydance Television",
    "Amblin Television", "Imagine Television", "Annapurna Pictures",
    "Plan B Entertainment", "Apatow Productions", "Bright/Kauffman/Crane",
    "Imagine Entertainment", "Studio Ghibli", "Toei Animation",
    "Madhouse", "Bones", "MAPPA", "Ufotable", "Pixar Television",
    "Walt Disney Animation", "Cartoon Network Studios", "Nickelodeon Animation",
    "Fox Television Animation", "DreamWorks Animation Television",
]

NOMBRES_ACTORES = [
    "Pedro", "Bella", "Daniel", "Cillian", "Jenna", "Aaron", "Pedro", "Helena",
    "Mark", "Anne", "Bryan", "Anna", "Kit", "Emilia", "Peter", "Sandra",
    "Bryan", "Sarah", "Steve", "Aubrey", "Jason", "Maya", "Henry", "Florence",
    "Jeffrey", "Elisabeth", "Adam", "Rebecca", "Walton", "Tatiana", "Patricia",
    "Jonathan", "Penelope", "Javier", "Isla", "Tom", "Nicole", "Ewan", "Naomi",
    "Donald", "Zazie", "Andrew", "Phoebe", "Hugh", "Jodie", "Bill", "Sigourney",
    "Idris", "Lashana", "John", "Regina", "Michael", "Hannah", "David", "Olivia",
    "Matt", "Saoirse", "Oscar", "Margot", "Joaquin", "Brie", "Robert", "Tessa",
    "Chris", "Letitia", "Anthony", "Lupita", "Mahershala", "Viola", "Sterling",
    "Tracee", "Issa", "Yvonne", "Zoë", "Constance", "Awkwafina", "Henry", "Ke",
    "Jamie", "Michelle", "Stephanie", "Quan", "Halle", "Daniel", "Pedro", "Jeremy",
    "Hailee", "Steven", "Chloé", "Gemma", "Diego", "Tenoch", "Yalitza", "Roma",
    "Demián", "Tessa", "Karla", "Alfonso", "Salma", "Eugenio", "Kate", "Antonio",
    "Penélope", "Eiza", "Alfonso", "Gael", "Diego", "Eva", "Wagner", "Sofía"
]

APELLIDOS_ACTORES = [
    "Pascal", "Ramsey", "Kaluuya", "Murphy", "Ortega", "Paul", "Almodóvar",
    "Bonham Carter", "Ruffalo", "Hathaway", "Cranston", "Torv", "Harington",
    "Clarke", "Dinklage", "Bullock", "Cranston", "Snook", "Carell", "Plaza",
    "Bateman", "Erskine", "Cavill", "Pugh", "Wright", "Moss", "Driver", "Hall",
    "Goggins", "Maslany", "Arquette", "Bailey", "Cruz", "Bardem", "Fisher",
    "Hiddleston", "Kidman", "McGregor", "Watts", "Glover", "Beetz", "Garfield",
    "Waller-Bridge", "Grant", "Comer", "Hader", "Weaver", "Elba", "Lynch",
    "Boyega", "King", "B. Jordan", "Einbinder", "Tennant", "Colman", "Smith",
    "Ronan", "Isaac", "Robbie", "Phoenix", "Larson", "Pattinson", "Thompson",
    "Hemsworth", "Wright", "Hopkins", "Nyong'o", "Ali", "Davis", "K. Brown",
    "Ellis Ross", "Rae", "Orji", "Kravitz", "Wu", "Lin", "Driver", "Huy Quan",
    "Lee Curtis", "Yeoh", "Hsu", "Stiller", "Berry", "Kaluuya", "Strong", "Renner",
    "Steinfeld", "Yeun", "Zhao", "Chan", "Luna", "Huerta", "Aparicio", "Ojeda",
    "Bichir", "Thompson", "Souza", "Cuarón", "Hayek", "Derbez", "del Castillo",
    "Banderas", "Cruz", "González", "Iñárritu", "García Bernal", "Luna", "Mendes",
    "Moura", "Vergara", "Carbonell"
]

NACIONALIDADES = [
    "Estadounidense", "Británica", "Canadiense", "Australiana", "Mexicana",
    "Española", "Argentina", "Chilena", "Brasileña", "Francesa", "Alemana",
    "Italiana", "Coreana", "Japonesa", "China", "India", "Surafricana",
    "Irlandesa", "Sueca", "Noruega", "Danesa", "Holandesa", "Belga",
    "Colombiana", "Venezolana", "Cubana", "Peruana", "Uruguaya", "Guatemalteca"
]

# Títulos plantilla para generar series únicas
TITULOS_BASE = [
    "The Last", "Dark", "Stranger", "Money", "House of", "Game of", "Breaking",
    "Better Call", "The Crown", "Black", "The Walking", "Westworld", "True",
    "Mr.", "Peaky", "The Marvelous", "The Boys", "The Mandalorian", "Loki",
    "Wanda", "Severance", "Foundation", "Ted", "Succession", "Euphoria",
    "Yellowjackets", "Wednesday", "Squid", "The Bear", "Andor", "Shogun",
    "Fallout", "Reacher", "Beef", "Daisy", "The White", "Killing", "Fleabag",
    "Sherlock", "Mindhunter", "Ozark", "Narcos", "El", "La", "Casa", "Vikings",
    "The Witcher", "Bridgerton", "Outlander", "Downton", "Chernobyl", "Atlanta",
    "Barry", "Hacks", "Only Murders", "What We", "Reservation", "Abbott", "Big",
    "Little", "Fargo", "True Detective", "Mare of", "The Sympathizer", "Shrinking",
    "The Diplomat", "Slow Horses", "Pachinko", "Tokyo", "Squid", "Crash", "Alice",
    "Lost", "Found", "Dark Side", "Light", "Beyond", "Inside", "Outside", "Above",
    "Below", "Through", "Across", "Among", "Within", "Without", "Beyond",
]

SUFIJOS = [
    "of Us", " Materials", "Things", "Heist", "the Dragon", "Thrones", "Bad",
    "Saul", " Mirror", "Dead", "Detective", "Robot", "Blinders", "Mrs. Maisel",
    "alorian", "Vision", " Ted", "Lasso", "ession", "ia", "Game", "Bear", "or",
    "lout", "f", "Jones", "Lotus", "Eve", "lock", "hunter", "k", "os", "Profesor",
    "Chefs", "Dynasty", "to Ashes", " Town", "Manor", "Tower", "of Cards"
]

# Sinopsis genéricas
SINOPSIS_BASE = [
    "Una historia épica que cambia el destino de los protagonistas para siempre.",
    "En un mundo donde las reglas se rompen, surgen héroes inesperados.",
    "Drama intenso sobre familia, lealtad y traición.",
    "Una mirada profunda a la condición humana en tiempos difíciles.",
    "Misterio y suspenso se entrelazan en esta serie cautivadora.",
    "Comedia que retrata la vida cotidiana con humor inteligente.",
    "Acción sin tregua en una aventura llena de giros inesperados.",
    "Romance que desafía las convenciones sociales de la época.",
    "Investigación criminal que pone a prueba los límites de la justicia.",
    "Una saga familiar que recorre generaciones y secretos.",
]


# ============================================
# GENERADORES
# ============================================

def fecha_aleatoria(inicio: date, fin: date) -> str:
    """Devuelve una fecha aleatoria en formato YYYY-MM-DD."""
    delta = (fin - inicio).days
    return (inicio + timedelta(days=random.randint(0, delta))).isoformat()


def generar_generos():
    """Genera el CSV de géneros."""
    rows = []
    for i, (nombre, desc) in enumerate(GENEROS_BASE, start=1):
        rows.append({
            "id": f"gen_{i:03d}",
            "nombre": nombre,
            "descripcion": desc,
            "popularidad": round(random.uniform(3.0, 9.5), 2),
            "tendencia": random.choice([True, False]),
            "anio": random.randint(1950, 2024),
        })
    return rows


def generar_plataformas():
    """Genera el CSV de plataformas."""
    rows = []
    for i, (nombre, pais, precio, fecha, subs) in enumerate(PLATAFORMAS_BASE, start=1):
        rows.append({
            "id": f"plat_{i:03d}",
            "nombre": nombre,
            "pais": pais,
            "precio": precio,
            "fechaFundacion": fecha,
            "suscriptores": subs,
        })
    return rows


def generar_estudios():
    """Genera el CSV de estudios de producción."""
    rows = []
    for i, nombre in enumerate(ESTUDIOS_BASE, start=1):
        anio_fund = random.randint(1920, 2015)
        rows.append({
            "id": f"est_{i:03d}",
            "nombre": nombre,
            "pais": random.choice(["Estados Unidos", "Reino Unido", "Canadá", "Japón"]),
            "anioFundacion": anio_fund,
            "activo": random.choice([True, True, True, False]),
            "presupuestoPromedio": round(random.uniform(5.0, 200.0), 2),
            "premios": random.randint(0, 150),
            "generosPrincipales": "|".join(random.sample(
                [g[0] for g in GENEROS_BASE], k=random.randint(2, 5)
            )),
        })
    return rows


def generar_actores(n=800):
    """Genera n actores. ~20% también serán directores."""
    rows = []
    nombres_usados = set()
    for i in range(1, n + 1):
        # Generar nombre único
        intentos = 0
        while True:
            nombre = f"{random.choice(NOMBRES_ACTORES)} {random.choice(APELLIDOS_ACTORES)}"
            if nombre not in nombres_usados or intentos > 5:
                break
            intentos += 1
        # Si sigue colisionando, agregar número
        if nombre in nombres_usados:
            nombre = f"{nombre} {i}"
        nombres_usados.add(nombre)

        # 20% son también directores (multi-label)
        es_director = random.random() < 0.20
        labels = "Actor|Director" if es_director else "Actor"

        rows.append({
            "id": f"act_{i:04d}",
            "labels": labels,
            "nombre": nombre,
            "nacionalidad": random.choice(NACIONALIDADES),
            "fechaNacimiento": fecha_aleatoria(date(1950, 1, 1), date(2005, 12, 31)),
            "premios": random.randint(0, 25),
            "activo": random.choice([True, True, True, False]),
            "popularidad": round(random.uniform(1.0, 10.0), 2),
            "papeles": "|".join(random.sample(
                ["Protagonista", "Antagonista", "Secundario", "Cameo", "Recurrente", "Invitado"],
                k=random.randint(1, 3)
            )),
        })
    return rows


def generar_series(n=3000):
    """Genera n series únicas."""
    rows = []
    titulos_usados = set()
    for i in range(1, n + 1):
        # Construir título único
        intentos = 0
        while True:
            titulo = f"{random.choice(TITULOS_BASE)} {random.choice(SUFIJOS)}".strip()
            if titulo not in titulos_usados or intentos > 5:
                break
            intentos += 1
        if titulo in titulos_usados:
            titulo = f"{titulo} {i}"
        titulos_usados.add(titulo)

        anio = random.randint(1990, 2024)
        rows.append({
            "id": f"ser_{i:04d}",
            "titulo": titulo,
            "sinopsis": random.choice(SINOPSIS_BASE),
            "anio": anio,
            "calificacion": round(random.uniform(4.0, 9.8), 2),
            "numTemporadas": random.randint(1, 12),
            "numEpisodios": random.randint(6, 200),
            "estadoEmision": random.choice([True, False]),
            "activa": random.choice([True, True, True, False]),
        })
    return rows


def generar_usuarios(n=800):
    """Genera n usuarios."""
    rows = []
    for i in range(1, n + 1):
        nombre_user = f"usuario_{i:04d}"
        rows.append({
            "id": f"usr_{i:04d}",
            "nombre": nombre_user,
            "email": f"{nombre_user}@ejemplo.com",
            "edad": random.randint(15, 75),
            "fechaRegistro": fecha_aleatoria(date(2020, 1, 1), date(2025, 4, 30)),
            "activo": random.choice([True, True, True, False]),
        })
    return rows


def generar_resenas(usuarios, series, n=1500):
    """Genera n reseñas escritas por usuarios sobre series."""
    rows = []
    etiquetas_pool = ["recomendada", "imprescindible", "decepcionante", "sobrevalorada",
                      "joya oculta", "clásico moderno", "apta para todos", "solo adultos"]
    for i in range(1, n + 1):
        rows.append({
            "id": f"res_{i:04d}",
            "usuario_id": random.choice(usuarios)["id"],
            "serie_id": random.choice(series)["id"],
            "texto": f"Reseña número {i}. " + random.choice(SINOPSIS_BASE),
            "puntuacion": random.randint(1, 10),
            "fecha": fecha_aleatoria(date(2022, 1, 1), date(2025, 4, 30)),
            "etiquetas": "|".join(random.sample(etiquetas_pool, k=random.randint(1, 3))),
            "util": random.randint(0, 500),
        })
    return rows


# ============================================
# GENERADORES DE RELACIONES
# ============================================

def generar_pertenece_a(series, generos):
    """Cada serie pertenece a 1-3 géneros. Uno es principal."""
    rows = []
    for serie in series:
        gens = random.sample(generos, k=random.randint(1, 3))
        for j, gen in enumerate(gens):
            rows.append({
                "serie_id": serie["id"],
                "genero_id": gen["id"],
                "esPrincipal": j == 0,
                "relevancia": round(random.uniform(0.3, 1.0), 2),
                "fechaAsignacion": fecha_aleatoria(date(2020, 1, 1), date(2025, 4, 30)),
            })
    return rows


def generar_transmite(plataformas, series):
    """Cada serie está en 1-3 plataformas."""
    rows = []
    regiones_pool = ["US", "MX", "ES", "GT", "AR", "BR", "CL", "CO", "PE", "UK", "FR", "DE", "JP"]
    for serie in series:
        plats = random.sample(plataformas, k=random.randint(1, 3))
        for plat in plats:
            rows.append({
                "plataforma_id": plat["id"],
                "serie_id": serie["id"],
                "fechaDisponible": fecha_aleatoria(date(2018, 1, 1), date(2025, 4, 30)),
                "exclusiva": random.choice([True, False]),
                "regiones": "|".join(random.sample(regiones_pool, k=random.randint(2, 6))),
            })
    return rows


def generar_produjo(estudios, series):
    """Cada serie es producida por 1 estudio."""
    rows = []
    for serie in series:
        est = random.choice(estudios)
        rows.append({
            "estudio_id": est["id"],
            "serie_id": serie["id"],
            "anio": serie["anio"],
            "presupuesto": round(random.uniform(2.0, 200.0), 2),
            "distribucion": random.choice(["Global", "Nacional", "Regional", "Streaming exclusivo"]),
        })
    return rows


def generar_actua_en(actores, series):
    """Cada serie tiene 3-8 actores. Cada actor está en 1-15 series."""
    rows = []
    personajes_pool = ["Protagonista A", "Protagonista B", "Antagonista Principal",
                       "Mentor", "Hijo/a", "Padre/Madre", "Amigo/a", "Detective",
                       "Médico", "Profesor", "Soldado", "Espía", "Líder", "Rebelde"]
    for serie in series:
        cast = random.sample(actores, k=random.randint(3, 8))
        for j, actor in enumerate(cast):
            temporadas = sorted(random.sample(
                range(1, serie["numTemporadas"] + 1),
                k=min(random.randint(1, serie["numTemporadas"]), serie["numTemporadas"])
            ))
            rows.append({
                "actor_id": actor["id"],
                "serie_id": serie["id"],
                "personaje": random.choice(personajes_pool),
                "protagonista": j < 2,
                "temporadas": "|".join(map(str, temporadas)),
            })
    return rows


def generar_dirige(actores, series):
    """Solo los actores con label Director dirigen series. 1-5 series cada uno."""
    rows = []
    directores = [a for a in actores if "Director" in a["labels"]]
    for director in directores:
        n_series = random.randint(1, 5)
        series_dirigidas = random.sample(series, k=n_series)
        for serie in series_dirigidas:
            temporadas = sorted(random.sample(
                range(1, serie["numTemporadas"] + 1),
                k=min(random.randint(1, serie["numTemporadas"]), serie["numTemporadas"])
            ))
            rows.append({
                "actor_id": director["id"],
                "serie_id": serie["id"],
                "temporadas": "|".join(map(str, temporadas)),
                "anioInicio": serie["anio"],
                "esPrincipal": random.choice([True, False]),
            })
    return rows


def generar_similar_a(series, max_por_serie=3):
    """Series similares entre sí. Bidireccional puede generarse implícito."""
    rows = []
    algoritmos = ["jaccard", "cosine", "manual", "collaborative"]
    pares_vistos = set()
    for serie in series:
        n = random.randint(0, max_por_serie)
        candidatas = random.sample(series, k=n + 5)
        contadas = 0
        for similar in candidatas:
            if similar["id"] == serie["id"]:
                continue
            par = tuple(sorted([serie["id"], similar["id"]]))
            if par in pares_vistos:
                continue
            pares_vistos.add(par)
            rows.append({
                "serie1_id": serie["id"],
                "serie2_id": similar["id"],
                "puntuacionSimilitud": round(random.uniform(0.4, 0.95), 2),
                "algoritmo": random.choice(algoritmos),
                "fechaCalculada": fecha_aleatoria(date(2024, 1, 1), date(2025, 4, 30)),
            })
            contadas += 1
            if contadas >= n:
                break
    return rows


def generar_vio(usuarios, series):
    """Cada usuario ha visto 5-30 series."""
    rows = []
    for usuario in usuarios:
        vistas = random.sample(series, k=random.randint(5, 30))
        for serie in vistas:
            porcentaje = round(random.uniform(0.1, 1.0), 2)
            rows.append({
                "usuario_id": usuario["id"],
                "serie_id": serie["id"],
                "fecha": fecha_aleatoria(date(2023, 1, 1), date(2025, 4, 30)),
                "porcentajeVisto": porcentaje,
                "completada": porcentaje >= 0.95,
            })
    return rows


def generar_le_gusta(vio_rows):
    """De las series vistas, ~40% le gustan al usuario."""
    rows = []
    for v in vio_rows:
        if random.random() < 0.4:
            rows.append({
                "usuario_id": v["usuario_id"],
                "serie_id": v["serie_id"],
                "fecha": v["fecha"],
                "puntuacion": round(random.uniform(6.0, 10.0), 2),
                "notificado": random.choice([True, False]),
            })
    return rows


def generar_en_lista(usuarios, series):
    """Cada usuario tiene 2-10 series en su lista de pendientes."""
    rows = []
    for usuario in usuarios:
        lista = random.sample(series, k=random.randint(2, 10))
        for j, serie in enumerate(lista):
            rows.append({
                "usuario_id": usuario["id"],
                "serie_id": serie["id"],
                "fechaAgregado": fecha_aleatoria(date(2024, 1, 1), date(2025, 4, 30)),
                "prioridad": random.randint(1, 5),
                "notificaciones": random.choice([True, False]),
            })
    return rows


def generar_sigue_a(usuarios):
    """Cada usuario sigue a 0-10 otros usuarios."""
    rows = []
    for usuario in usuarios:
        n = random.randint(0, 10)
        seguidos = random.sample(
            [u for u in usuarios if u["id"] != usuario["id"]],
            k=n
        )
        for seguido in seguidos:
            rows.append({
                "usuario1_id": usuario["id"],
                "usuario2_id": seguido["id"],
                "fechaSeguimiento": fecha_aleatoria(date(2023, 1, 1), date(2025, 4, 30)),
                "mutuo": random.choice([True, False]),
                "notificaciones": random.choice([True, False]),
            })
    return rows


def generar_escribio_y_sobre(resenas):
    """A partir de las reseñas, genera ESCRIBIÓ (Usuario→Reseña) y SOBRE (Reseña→Serie)."""
    escribio = []
    sobre = []
    visibilidades = ["publica", "amigos", "privada"]
    for r in resenas:
        escribio.append({
            "usuario_id": r["usuario_id"],
            "resena_id": r["id"],
            "fecha": r["fecha"],
            "editada": random.choice([True, False]),
            "visibilidad": random.choice(visibilidades),
        })
        sobre.append({
            "resena_id": r["id"],
            "serie_id": r["serie_id"],
            "verificada": random.choice([True, False]),
            "temporadaResenada": random.randint(1, 5),
            "contieneSpoilers": random.choice([True, False]),
        })
    return escribio, sobre


# ============================================
# ESCRITURA DE CSVs
# ============================================

def escribir_csv(filename, rows, fieldnames):
    """Escribe un CSV con los headers correctos."""
    path = OUT_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  {filename}: {len(rows)} filas")


def main():
    print("Generando datos sintéticos coherentes...")
    print()

    # NODOS
    print("Nodos:")
    generos = generar_generos()
    escribir_csv("generos.csv", generos,
                 ["id", "nombre", "descripcion", "popularidad", "tendencia", "anio"])

    plataformas = generar_plataformas()
    escribir_csv("plataformas.csv", plataformas,
                 ["id", "nombre", "pais", "precio", "fechaFundacion", "suscriptores"])

    estudios = generar_estudios()
    escribir_csv("estudios.csv", estudios,
                 ["id", "nombre", "pais", "anioFundacion", "activo",
                  "presupuestoPromedio", "premios", "generosPrincipales"])

    actores = generar_actores(800)
    escribir_csv("actores.csv", actores,
                 ["id", "labels", "nombre", "nacionalidad", "fechaNacimiento",
                  "premios", "activo", "popularidad", "papeles"])

    series = generar_series(3000)
    escribir_csv("series.csv", series,
                 ["id", "titulo", "sinopsis", "anio", "calificacion",
                  "numTemporadas", "numEpisodios", "estadoEmision", "activa"])

    usuarios = generar_usuarios(800)
    escribir_csv("usuarios.csv", usuarios,
                 ["id", "nombre", "email", "edad", "fechaRegistro", "activo"])

    resenas = generar_resenas(usuarios, series, 1500)
    escribir_csv("resenas.csv", resenas,
                 ["id", "usuario_id", "serie_id", "texto", "puntuacion",
                  "fecha", "etiquetas", "util"])

    print()
    print("Relaciones:")

    # RELACIONES
    pertenece_a = generar_pertenece_a(series, generos)
    escribir_csv("rel_pertenece_a.csv", pertenece_a,
                 ["serie_id", "genero_id", "esPrincipal", "relevancia", "fechaAsignacion"])

    transmite = generar_transmite(plataformas, series)
    escribir_csv("rel_transmite.csv", transmite,
                 ["plataforma_id", "serie_id", "fechaDisponible", "exclusiva", "regiones"])

    produjo = generar_produjo(estudios, series)
    escribir_csv("rel_produjo.csv", produjo,
                 ["estudio_id", "serie_id", "anio", "presupuesto", "distribucion"])

    actua_en = generar_actua_en(actores, series)
    escribir_csv("rel_actua_en.csv", actua_en,
                 ["actor_id", "serie_id", "personaje", "protagonista", "temporadas"])

    dirige = generar_dirige(actores, series)
    escribir_csv("rel_dirige.csv", dirige,
                 ["actor_id", "serie_id", "temporadas", "anioInicio", "esPrincipal"])

    similar_a = generar_similar_a(series, max_por_serie=3)
    escribir_csv("rel_similar_a.csv", similar_a,
                 ["serie1_id", "serie2_id", "puntuacionSimilitud", "algoritmo", "fechaCalculada"])

    vio = generar_vio(usuarios, series)
    escribir_csv("rel_vio.csv", vio,
                 ["usuario_id", "serie_id", "fecha", "porcentajeVisto", "completada"])

    le_gusta = generar_le_gusta(vio)
    escribir_csv("rel_le_gusta.csv", le_gusta,
                 ["usuario_id", "serie_id", "fecha", "puntuacion", "notificado"])

    en_lista = generar_en_lista(usuarios, series)
    escribir_csv("rel_en_lista.csv", en_lista,
                 ["usuario_id", "serie_id", "fechaAgregado", "prioridad", "notificaciones"])

    sigue_a = generar_sigue_a(usuarios)
    escribir_csv("rel_sigue_a.csv", sigue_a,
                 ["usuario1_id", "usuario2_id", "fechaSeguimiento", "mutuo", "notificaciones"])

    escribio, sobre = generar_escribio_y_sobre(resenas)
    escribir_csv("rel_escribio.csv", escribio,
                 ["usuario_id", "resena_id", "fecha", "editada", "visibilidad"])
    escribir_csv("rel_sobre.csv", sobre,
                 ["resena_id", "serie_id", "verificada", "temporadaResenada", "contieneSpoilers"])

    # RESUMEN
    print()
    total_nodos = (len(generos) + len(plataformas) + len(estudios) +
                   len(actores) + len(series) + len(usuarios) + len(resenas))
    total_rels = (len(pertenece_a) + len(transmite) + len(produjo) +
                  len(actua_en) + len(dirige) + len(similar_a) + len(vio) +
                  len(le_gusta) + len(en_lista) + len(sigue_a) +
                  len(escribio) + len(sobre))
    print("=" * 50)
    print(f"TOTAL NODOS: {total_nodos}")
    print(f"TOTAL RELACIONES: {total_rels}")
    print(f"Multi-label (Actor:Director): {sum(1 for a in actores if 'Director' in a['labels'])}")
    print("=" * 50)
    print("Listo. Los CSVs están en la carpeta data/")


if __name__ == "__main__":
    main()
