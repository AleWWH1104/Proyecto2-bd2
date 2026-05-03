# Motor de Recomendación de Series - Neo4j

Proyecto 2 - CC3089 Base de Datos 2 - Universidad del Valle de Guatemala

API REST que implementa un motor de recomendación de series usando Neo4j como base de datos orientada a grafos.

## Stack

- **Python 3.11+**
- **FastAPI** — backend con documentación interactiva (Swagger)
- **Neo4j 5** — base de datos de grafos (local con Docker o en AuraDB)
- **uv** — gestor de paquetes y entornos virtuales

## Requisitos previos

- [Python 3.11+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (para Neo4j local)

### Instalar uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Setup del proyecto

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd proyecto-series-neo4j
```

### 2. Crear archivo `.env`

Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

Por defecto está configurado para Neo4j local con Docker. Si vas a usar Aura, comenta las líneas de local y descomenta las de Aura.

### 3. Instalar dependencias

```bash
uv sync
```

Esto crea el entorno virtual `.venv` automáticamente e instala todo lo necesario.

### 4. Levantar Neo4j local con Docker

```bash
docker compose up -d
```

Esto inicia un contenedor de Neo4j en segundo plano. Puedes verificar que está corriendo:

```bash
docker compose ps
```

Para verlo en el navegador, abre [http://localhost:7474](http://localhost:7474) (usuario: `neo4j`, password: `password123`).

### 5. Poblar la base de datos

Genera los CSVs (solo la primera vez):

```bash
cd data && python3 generar_datos.py && cd ..
```

Carga los datos a Neo4j:

```bash
uv run python scripts/seed.py
```

Esto carga ~6,200 nodos y ~68,900 relaciones.

### 6. Levantar el backend

```bash
uv run uvicorn app.main:app --reload
```

Abre en el navegador:

- **API**: [http://localhost:8000](http://localhost:8000)
- **Swagger UI** (documentación interactiva): [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health check**: [http://localhost:8000/health](http://localhost:8000/health)

## Comandos útiles

```bash
# Levantar el backend
uv run uvicorn app.main:app --reload

# Poblar la BD
uv run python scripts/seed.py

# Borrar todos los datos de la BD
uv run python scripts/reset.py

# Generar CSVs nuevos
cd data && python3 generar_datos.py

# Agregar una dependencia nueva
uv add nombre-paquete

# Levantar Neo4j local
docker compose up -d

# Detener Neo4j local
docker compose down

# Ver logs de Neo4j
docker compose logs -f neo4j

# Borrar Neo4j local (incluye datos)
docker compose down -v
```

## Estructura del proyecto

```
proyecto-series-neo4j/
├── app/
│   ├── main.py              # Entry point FastAPI
│   ├── config.py            # Variables de entorno
│   ├── database.py          # Conexión Neo4j
│   ├── models.py            # Schemas Pydantic
│   ├── repositories/        # Queries Cypher
│   └── routers/             # Endpoints HTTP
├── data/                    # CSVs de datos
│   └── generar_datos.py     # Generador de datos sintéticos
├── scripts/
│   ├── seed.py              # Pobla la BD
│   └── reset.py             # Borra todo
├── docker-compose.yml       # Neo4j local
├── pyproject.toml           # Dependencias (uv)
├── .env                     # Variables (no se sube a git)
└── .env.example             # Plantilla del .env
```

## Modelo de datos

### Nodos (7 etiquetas)

| Etiqueta | Descripción |
|---|---|
| `Serie` | Series de TV |
| `Usuario` | Usuarios de la plataforma |
| `Actor` | Actores |
| `Director` | Multi-label, actores que también dirigen |
| `Genero` | Géneros (drama, comedia, etc.) |
| `Plataforma` | Servicios de streaming |
| `EstudioProduccion` | Estudios productores |
| `Resena` | Reseñas escritas por usuarios |

### Relaciones (11 tipos)

| Relación | Origen → Destino |
|---|---|
| `PERTENECE_A` | Serie → Genero |
| `TRANSMITE` | Plataforma → Serie |
| `SIMILAR_A` | Serie → Serie |
| `VIO` | Usuario → Serie |
| `LE_GUSTA` | Usuario → Serie |
| `EN_LISTA` | Usuario → Serie |
| `ESCRIBIO` | Usuario → Resena |
| `SOBRE` | Resena → Serie |
| `ACTUA_EN` | Actor → Serie |
| `DIRIGE` | Director → Serie |
| `PRODUJO` | EstudioProduccion → Serie |
| `SIGUE_A` | Usuario → Usuario |

## Cambiar de Neo4j local a Aura

1. Crea una instancia gratuita en [console.neo4j.io](https://console.neo4j.io)
2. Guarda las credenciales que te da Aura
3. Edita el archivo `.env`:
   - Comenta las líneas de **LOCAL**
   - Descomenta las de **AURA** y pon tus credenciales reales
4. Vuelve a correr `uv run python scripts/seed.py` para poblar Aura
5. Levanta el backend normalmente: `uv run uvicorn app.main:app --reload`

## Equipo

Por completar
