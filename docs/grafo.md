# Grafo del proyecto

Este documento describe el contrato real del grafo segun `scripts/seed.py`.

## Convencion de nombres

- En el codigo se usa naming ASCII.
- La fuente de verdad tecnica para labels, propiedades y relaciones es `scripts/seed.py`.
- Ejemplos: `anio`, `puntuacion`, `ACTUA_EN`, `ESCRIBIO`, `Resena`.

## Nodos (labels) y propiedades

### `:Serie`

- `id`: String
- `titulo`: String
- `sinopsis`: String
- `anio`: Integer
- `calificacion`: Float
- `numTemporadas`: Integer
- `numEpisodios`: Integer
- `estadoEmision`: Boolean
- `activa`: Boolean

### `:Genero`

- `id`: String
- `nombre`: String
- `descripcion`: String
- `popularidad`: Float
- `tendencia`: Boolean
- `anio`: Integer

### `:Plataforma`

- `id`: String
- `nombre`: String
- `pais`: String
- `precio`: Float
- `fechaFundacion`: Date
- `suscriptores`: Integer

### `:EstudioProduccion`

- `id`: String
- `nombre`: String
- `pais`: String
- `anioFundacion`: Integer
- `activo`: Boolean
- `presupuestoPromedio`: Float
- `premios`: Integer
- `generosPrincipales`: List[String]

### `:Actor`

- `id`: String
- `nombre`: String
- `nacionalidad`: String
- `fechaNacimiento`: Date
- `premios`: Integer
- `activo`: Boolean
- `popularidad`: Float
- `papeles`: List[String]

### `:Actor:Director`

Algunos actores tambien tienen el label adicional `:Director`.

Propiedades:

- `id`: String
- `nombre`: String
- `nacionalidad`: String
- `fechaNacimiento`: Date
- `premios`: Integer
- `activo`: Boolean
- `popularidad`: Float
- `papeles`: List[String]

### `:Usuario`

- `id`: String
- `nombre`: String
- `email`: String
- `edad`: Integer
- `fechaRegistro`: Date
- `activo`: Boolean

### `:Resena`

- `id`: String
- `texto`: String
- `puntuacion`: Integer
- `fecha`: Date
- `etiquetas`: List[String]
- `util`: Integer

## Relaciones y propiedades

### Relaciones con series

#### `(Serie)-[:PERTENECE_A]->(Genero)`

- `esPrincipal`: Boolean
- `relevancia`: Float
- `fechaAsignacion`: Date

#### `(Plataforma)-[:TRANSMITE]->(Serie)`

- `fechaDisponible`: Date
- `exclusiva`: Boolean
- `regiones`: List[String]

#### `(EstudioProduccion)-[:PRODUJO]->(Serie)`

- `anio`: Integer
- `presupuesto`: Float
- `distribucion`: String

#### `(Actor)-[:ACTUA_EN]->(Serie)`

- `personaje`: String
- `protagonista`: Boolean
- `temporadas`: List[Integer]

#### `(Director)-[:DIRIGE]->(Serie)`

- `temporadas`: List[Integer]
- `anioInicio`: Integer
- `esPrincipal`: Boolean

#### `(Serie)-[:SIMILAR_A]->(Serie)`

- `puntuacionSimilitud`: Float
- `algoritmo`: String
- `fechaCalculada`: Date

### Relaciones de usuario e interacciones

#### `(Usuario)-[:VIO]->(Serie)`

- `fecha`: Date
- `porcentajeVisto`: Float
- `completada`: Boolean

#### `(Usuario)-[:LE_GUSTA]->(Serie)`

- `fecha`: Date
- `puntuacion`: Float
- `notificado`: Boolean

#### `(Usuario)-[:EN_LISTA]->(Serie)`

- `fechaAgregado`: Date
- `prioridad`: Integer
- `notificaciones`: Boolean

#### `(Usuario)-[:SIGUE_A]->(Usuario)`

- `fechaSeguimiento`: Date
- `mutuo`: Boolean
- `notificaciones`: Boolean

#### `(Usuario)-[:ESCRIBIO]->(Resena)`

- `fecha`: Date
- `editada`: Boolean
- `visibilidad`: String

#### `(Resena)-[:SOBRE]->(Serie)`

- `verificada`: Boolean
- `temporadaResenada`: Integer
- `contieneSpoilers`: Boolean

## Resumen de compatibilidad con el seed

- Labels usados por el seed: `Serie`, `Genero`, `Plataforma`, `EstudioProduccion`, `Actor`, `Director`, `Usuario`, `Resena`
- Relaciones usadas por el seed: `PERTENECE_A`, `TRANSMITE`, `PRODUJO`, `ACTUA_EN`, `DIRIGE`, `SIMILAR_A`, `VIO`, `LE_GUSTA`, `EN_LISTA`, `SIGUE_A`, `ESCRIBIO`, `SOBRE`
- Todas las entidades cargadas por `seed.py` incluyen `id` como identificador funcional.
