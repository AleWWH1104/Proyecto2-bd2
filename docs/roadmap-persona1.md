# Roadmap Persona 1

Roadmap de implementacion para Persona 1: Series + catalogos + relaciones centradas en `Serie`.

Este documento esta alineado con:

- `docs/grafo.md`
- `scripts/seed.py`
- `app/models.py`
- la rubrica del proyecto Neo4j

## Objetivo

Implementar los 19 endpoints de Persona 1 sobre el backend FastAPI actual, usando Neo4j como fuente de datos y respetando el contrato real del seed.

## Regla tecnica base

La fuente de verdad del contrato del grafo es `scripts/seed.py`.

Se debe usar naming ASCII en codigo, schemas y Cypher:

- `anio`
- `puntuacion`
- `Resena`
- `ACTUA_EN`
- `ESCRIBIO`

No mezclar nombres del PDF con nombres del seed.

## Alcance de Persona 1

### Series

1. `GET /series`
2. `GET /series/{id}`
3. `POST /series`
4. `PATCH /series/{id}`
5. `PATCH /series/masivo`
6. `DELETE /series/{id}/propiedades`
7. `DELETE /series/{id}`
8. `DELETE /series`

### Generos

1. `GET /generos`
2. `POST /generos`

### Plataformas

1. `GET /plataformas`
2. `POST /plataformas`

### Relaciones

1. `POST /relaciones/pertenece-a/{serie_id}/{genero_id}`
2. `PATCH /relaciones/pertenece-a/{serie_id}/{genero_id}`
3. `DELETE /relaciones/pertenece-a/{serie_id}/{genero_id}`
4. `POST /relaciones/transmite/{plataforma_id}/{serie_id}`
5. `POST /relaciones/similar-a/{serie1_id}/{serie2_id}`

### Consultas Cypher

1. `GET /consultas/series-mejor-calificadas-por-genero`
2. `GET /consultas/plataformas-mas-exclusivas`

## Estado actual del repositorio

- `app/models.py` tiene solo modelos base para operaciones genericas.
- `app/routers/series.py` existe como stub.
- `app/routers/generos.py` existe como stub.
- `app/routers/plataformas.py` existe como stub.
- `app/routers/relaciones.py` existe como stub.
- `app/routers/consultas.py` existe como stub.
- `app/repositories/*.py` de Persona 1 estan vacios.
- `app/main.py` aun no registra routers.

Conclusion: Persona 1 debe implementarse por capas, no por endpoint aislado.

## Fase 1. Cerrar contrato de schemas

Archivo principal:

- `app/models.py`

### Schemas de Serie

Crear estos modelos:

- `SerieBase`
- `SerieCreate`
- `SeriePatch`
- `SerieResponse`
- `SerieDetalleResponse`
- `SerieListItem`
- `SerieListResponse`

Propiedades del nodo `Serie`:

- `id: str | None`
- `titulo: str`
- `sinopsis: str`
- `anio: int`
- `calificacion: float`
- `numTemporadas: int`
- `numEpisodios: int`
- `estadoEmision: bool`
- `activa: bool`

### Schemas de filtros para `GET /series`

Crear un modelo o parametros equivalentes para:

- `titulo`
- `anio`
- `calificacion_min`
- `calificacion_max`
- `activa`
- `estadoEmision`
- `genero_id`
- `plataforma_id`
- `limit`
- `skip`

### Schemas de agregacion para `GET /series`

Crear modelos para responder:

- total de series
- promedio de calificacion
- conteo por genero
- conteo por plataforma

Sugeridos:

- `ConteoPorNombre`
- `SeriesAggregations`

### Schemas de Genero

- `GeneroBase`
- `GeneroCreate`
- `GeneroResponse`

Propiedades del nodo `Genero`:

- `id: str | None`
- `nombre: str`
- `descripcion: str`
- `popularidad: float`
- `tendencia: bool`
- `anio: int`

### Schemas de Plataforma

- `PlataformaBase`
- `PlataformaCreate`
- `PlataformaResponse`

Propiedades del nodo `Plataforma`:

- `id: str | None`
- `nombre: str`
- `pais: str`
- `precio: float`
- `fechaFundacion: date`
- `suscriptores: int`

### Schemas de relaciones

Crear:

- `PerteneceABase`
- `PerteneceACreate`
- `PerteneceAPatch`
- `TransmiteCreate`
- `SimilarACreate`

Propiedades por relacion:

`PERTENECE_A`

- `esPrincipal: bool`
- `relevancia: float`
- `fechaAsignacion: date`

`TRANSMITE`

- `fechaDisponible: date`
- `exclusiva: bool`
- `regiones: list[str]`

`SIMILAR_A`

- `puntuacionSimilitud: float`
- `algoritmo: str`
- `fechaCalculada: date`

### Schemas de operaciones masivas

Reusar y/o extender:

- `IdsRequest`
- `PropiedadesRequest`
- `PropiedadesMasivoRequest`
- `EliminarPropiedadesRequest`

Si hace falta mas precision, crear:

- `SeriesMasivoPatchRequest`

## Fase 2. Repository de Series

Archivo:

- `app/repositories/series.py`

Implementar funciones:

- `listar_series(...)`
- `obtener_serie_por_id(serie_id)`
- `crear_serie(data)`
- `actualizar_propiedades_serie(serie_id, propiedades)`
- `actualizar_propiedades_series_masivo(ids, propiedades)`
- `eliminar_propiedades_serie(serie_id, nombres)`
- `eliminar_serie(serie_id)`
- `eliminar_series(ids)`

### Reglas Cypher

`GET /series`

- usar `MATCH (s:Serie)`
- agregar `OPTIONAL MATCH` para genero y plataforma si se necesitan filtros o agregaciones
- construir `WHERE` dinamico solo con filtros presentes
- devolver lista + bloque de agregaciones

`PATCH /series/masivo`

- usar `UNWIND $ids AS serie_id`

`DELETE /series/{id}` y `DELETE /series`

- usar `DETACH DELETE`

`DELETE /series/{id}/propiedades`

- eliminar keys especificas del nodo, no el nodo completo

## Fase 3. Router de Series

Archivo:

- `app/routers/series.py`

Exponer endpoints:

- `GET /series`
- `GET /series/{id}`
- `POST /series`
- `PATCH /series/{id}`
- `PATCH /series/masivo`
- `DELETE /series/{id}/propiedades`
- `DELETE /series/{id}`
- `DELETE /series`

### Criterios de validacion

- `POST` debe crear una serie con al menos 5 propiedades configuradas
- `GET /series` debe cubrir filtros + agregaciones
- `PATCH` debe servir tanto para agregar como actualizar propiedades
- `PATCH /series/masivo` debe demostrar operacion masiva de nodos
- `DELETE /series` debe recibir body con multiples IDs

## Fase 4. Catalogos de apoyo

Archivos:

- `app/repositories/generos.py`
- `app/routers/generos.py`
- `app/repositories/plataformas.py`
- `app/routers/plataformas.py`

### Generos

Funciones:

- `listar_generos()`
- `crear_genero(data)`

Endpoints:

- `GET /generos`
- `POST /generos`

### Plataformas

Funciones:

- `listar_plataformas()`
- `crear_plataforma(data)`

Endpoints:

- `GET /plataformas`
- `POST /plataformas`

## Fase 5. Relaciones centradas en Serie

Archivo:

- `app/repositories/relaciones.py`
- `app/routers/relaciones.py`

Implementar funciones:

- `crear_pertenece_a(serie_id, genero_id, data)`
- `actualizar_pertenece_a(serie_id, genero_id, propiedades)`
- `eliminar_pertenece_a(serie_id, genero_id)`
- `crear_transmite(plataforma_id, serie_id, data)`
- `crear_similar_a(serie1_id, serie2_id, data)`

### Regla importante

Antes de crear una relacion, validar que ambos nodos existan.

### Endpoints

- `POST /relaciones/pertenece-a/{serie_id}/{genero_id}`
- `PATCH /relaciones/pertenece-a/{serie_id}/{genero_id}`
- `DELETE /relaciones/pertenece-a/{serie_id}/{genero_id}`
- `POST /relaciones/transmite/{plataforma_id}/{serie_id}`
- `POST /relaciones/similar-a/{serie1_id}/{serie2_id}`

### Cobertura de rubrica

- creacion de relacion con 3 propiedades
- actualizacion de propiedades de una relacion
- eliminacion de una relacion

## Fase 6. Consultas Cypher de Persona 1

Archivos:

- `app/repositories/consultas.py`
- `app/routers/consultas.py`

### Consulta 1

Endpoint:

- `GET /consultas/series-mejor-calificadas-por-genero`

Debe usar:

- `MATCH`
- `WITH`
- `ORDER BY`
- agregacion por genero

Respuesta sugerida:

- genero
- top series
- promedio de calificacion
- cantidad de series evaluadas

### Consulta 2

Endpoint:

- `GET /consultas/plataformas-mas-exclusivas`

Debe usar:

- `MATCH`
- `WHERE r.exclusiva = true`
- `COUNT`
- `ORDER BY`

Respuesta sugerida:

- plataforma
- total exclusivas
- total series
- porcentaje exclusivas

## Fase 7. Registro en FastAPI

Archivo:

- `app/main.py`

Acciones:

- importar routers reales
- registrar `series.router`
- registrar `generos.router`
- registrar `plataformas.router`
- registrar `relaciones.router`
- registrar `consultas.router`

Sin esto, Swagger no mostrara Persona 1.

## Matriz endpoint -> repository -> Cypher

| Endpoint | Repository | Operacion Cypher base |
|---|---|---|
| `GET /series` | `series.listar_series` | `MATCH (s:Serie)` + filtros + agregaciones |
| `GET /series/{id}` | `series.obtener_serie_por_id` | `MATCH (s:Serie {id: $id})` + relaciones opcionales |
| `POST /series` | `series.crear_serie` | `CREATE (s:Serie {...})` |
| `PATCH /series/{id}` | `series.actualizar_propiedades_serie` | `MATCH (s:Serie {id: $id}) SET s += $propiedades` |
| `PATCH /series/masivo` | `series.actualizar_propiedades_series_masivo` | `UNWIND $ids AS id MATCH (s:Serie {id: id}) SET s += $propiedades` |
| `DELETE /series/{id}/propiedades` | `series.eliminar_propiedades_serie` | `MATCH (s:Serie {id: $id}) REMOVE ...` |
| `DELETE /series/{id}` | `series.eliminar_serie` | `MATCH (s:Serie {id: $id}) DETACH DELETE s` |
| `DELETE /series` | `series.eliminar_series` | `UNWIND $ids AS id MATCH (s:Serie {id: id}) DETACH DELETE s` |
| `GET /generos` | `generos.listar_generos` | `MATCH (g:Genero)` |
| `POST /generos` | `generos.crear_genero` | `CREATE (g:Genero {...})` |
| `GET /plataformas` | `plataformas.listar_plataformas` | `MATCH (p:Plataforma)` |
| `POST /plataformas` | `plataformas.crear_plataforma` | `CREATE (p:Plataforma {...})` |
| `POST /relaciones/pertenece-a/{serie_id}/{genero_id}` | `relaciones.crear_pertenece_a` | `MATCH ... CREATE/MERGE (s)-[r:PERTENECE_A]->(g)` |
| `PATCH /relaciones/pertenece-a/{serie_id}/{genero_id}` | `relaciones.actualizar_pertenece_a` | `MATCH (s)-[r:PERTENECE_A]->(g) SET r += $propiedades` |
| `DELETE /relaciones/pertenece-a/{serie_id}/{genero_id}` | `relaciones.eliminar_pertenece_a` | `MATCH (s)-[r:PERTENECE_A]->(g) DELETE r` |
| `POST /relaciones/transmite/{plataforma_id}/{serie_id}` | `relaciones.crear_transmite` | `MATCH ... CREATE/MERGE (p)-[r:TRANSMITE]->(s)` |
| `POST /relaciones/similar-a/{serie1_id}/{serie2_id}` | `relaciones.crear_similar_a` | `MATCH ... CREATE/MERGE (s1)-[r:SIMILAR_A]->(s2)` |
| `GET /consultas/series-mejor-calificadas-por-genero` | `consultas.series_mejor_calificadas_por_genero` | `MATCH (s)-[:PERTENECE_A]->(g)` + `AVG/ORDER BY` |
| `GET /consultas/plataformas-mas-exclusivas` | `consultas.plataformas_mas_exclusivas` | `MATCH (p)-[r:TRANSMITE]->(s)` + `COUNT/ORDER BY` |

## Orden exacto recomendado

1. `app/models.py`
2. `app/repositories/series.py`
3. `app/routers/series.py`
4. `app/repositories/generos.py`
5. `app/routers/generos.py`
6. `app/repositories/plataformas.py`
7. `app/routers/plataformas.py`
8. `app/repositories/relaciones.py`
9. `app/routers/relaciones.py`
10. `app/repositories/consultas.py`
11. `app/routers/consultas.py`
12. `app/main.py`

## Checklist de cierre

- `docs/grafo.md` alineado con `seed.py`
- schemas de Persona 1 definidos en `app/models.py`
- repositories de Persona 1 implementados
- routers de Persona 1 implementados
- routers registrados en `app/main.py`
- Swagger muestra los 19 endpoints
- `GET /series` demuestra filtros + agregaciones
- existe operacion masiva de nodos en `PATCH /series/masivo`
- existe eliminacion masiva de nodos en `DELETE /series`
- `PERTENECE_A` demuestra gestion de propiedades de una relacion
- las 2 consultas Cypher de Persona 1 funcionan con datos del seed

## Siguiente paso recomendado

Empezar por `app/models.py` y dejar cerrados todos los schemas de Persona 1 antes de tocar routers o queries.
