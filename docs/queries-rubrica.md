# Queries Rúbrica — Proyecto 2 Neo4j

**Base URL:** `http://localhost:8000`  
**IDs de referencia útiles:**
- Serie: `ser_0015`, `ser_0864`, `ser_1526`, `ser_2511`
- Usuario: `usr_0655`, `usr_0037`, `usr_0386`
- Actor: `act_0344`, `act_0549`
- Genero: `gen_040` (Variedades), `gen_020` (Sobrenatural)
- Plataforma: `plat_008` (Peacock), `plat_001` (Netflix)

---

## ESTADO RÚBRICA

| Categoría | Criterio | Pts | Estado |
|-----------|----------|-----|--------|
| Modelado | Caso de uso: Motor de recomendación | 5 | ✅ |
| Modelado | 5+ labels / 5+ props por label | 5 | ✅ 8 labels |
| Modelado | 10+ tipos de relaciones / 3+ props | 5 | ✅ 12 relaciones |
| Modelado | Todos los tipos de datos | 5 | ✅ |
| Set de datos | Carga CSV | 5 | ✅ |
| Set de datos | Datos pre-cargados | 2 | ✅ |
| Set de datos | 5000+ nodos distintos | 2 | ✅ |
| Set de datos | Grafo conexo | 1 | ✅ |
| Funcional | Crear nodo 1 label | 5 | ✅ |
| Funcional | Crear nodo 2+ labels | 5 | ✅ Actor:Director |
| Funcional | Crear nodo 5+ propiedades | 5 | ✅ Serie (9 props) |
| Funcional | Visualización: 1 nodo, muchos, agregaciones, filtros | 5 | ✅ |
| Funcional | Gestión props nodos (add/update/delete × 1 y masivo) | 10 | ✅ |
| Funcional | Crear relación con 3+ propiedades | 5 | ✅ |
| Funcional | Gestión relaciones (add/update/delete × 1 y masivo) | 10 | ✅ |
| Funcional | Eliminar 1 nodo | 5 | ✅ |
| Funcional | Eliminar múltiples nodos | 5 | ✅ |
| Funcional | Eliminar 1 relación | 5 | ✅ |
| Funcional | Eliminar múltiples relaciones | 5 | ✅ |
| Funcional | Consultas Cypher (4-6, 2/persona) | 15 | ✅ 6 queries |
| Extra | Algoritmo Data Science (Jaccard Similarity) | 10 | ✅ |

✅ **Todos los criterios implementados y verificados.**

---

## 1. MODELADO — DEMOSTRACIÓN DE LABELS Y TIPOS DE DATOS

### Labels implementados
```
:Serie              → String, Float, Integer, Boolean
:Genero             → String, Float, Integer, Boolean
:Plataforma         → String, Float, Integer, Date
:EstudioProduccion  → String, Float, Integer, Boolean, List[String]
:Actor              → String, Float, Integer, Date, List[String]
:Actor:Director     → multi-label (mismo nodo, 2 labels)
:Usuario            → String, Integer, Boolean, Date
:Resena             → String, Integer, List[String], Date
```

### Relaciones implementadas (12)
```
(Serie)-[:PERTENECE_A]->(Genero)         → esPrincipal:Boolean, relevancia:Float, fechaAsignacion:Date
(Plataforma)-[:TRANSMITE]->(Serie)       → fechaDisponible:Date, exclusiva:Boolean, regiones:List
(EstudioProduccion)-[:PRODUJO]->(Serie)  → anio:Integer, presupuesto:Float, distribucion:String
(Actor)-[:ACTUA_EN]->(Serie)             → personaje:String, protagonista:Boolean, temporadas:List
(Director)-[:DIRIGE]->(Serie)            → temporadas:List, anioInicio:Integer, esPrincipal:Boolean
(Serie)-[:SIMILAR_A]->(Serie)            → puntuacionSimilitud:Float, algoritmo:String, fechaCalculada:Date
(Usuario)-[:VIO]->(Serie)                → fecha:Date, porcentajeVisto:Float, completada:Boolean
(Usuario)-[:LE_GUSTA]->(Serie)           → fecha:Date, puntuacion:Float, notificado:Boolean
(Usuario)-[:EN_LISTA]->(Serie)           → fechaAgregado:Date, prioridad:Integer, notificaciones:Boolean
(Usuario)-[:SIGUE_A]->(Usuario)          → fechaSeguimiento:Date, mutuo:Boolean, notificaciones:Boolean
(Usuario)-[:ESCRIBIO]->(Resena)          → fecha:Date, editada:Boolean, visibilidad:String
(Resena)-[:SOBRE]->(Serie)               → verificada:Boolean, temporadaResenada:Integer, contieneSpoilers:Boolean
```

---

## 2. SET DE DATOS — CARGA CSV

### Cargar todos los CSVs desde data/
```bash
curl -X POST http://localhost:8000/admin/cargar-csv
```
**Cypher generado internamente:**
```cypher
MERGE (n:Genero {id: row.id}) SET n += {nombre: row.nombre, ...}
MERGE (n:Serie {id: row.id}) SET n += {...}
-- etc. para cada tipo
```

### Subir CSV personalizado (nodos nuevos)
```bash
curl -X POST http://localhost:8000/admin/subir-csv \
  -F "tipo=series" \
  -F "file=@ruta/al/archivo.csv"
```

---

## 3. CREAR NODOS

### 3.1 Crear nodo con 1 label (Usuario)
**Rúbrica:** Crear nodo 1 label + 5+ propiedades

```bash
curl -X POST http://localhost:8000/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Maria Lopez",
    "email": "maria@test.com",
    "edad": 28,
    "activo": true
  }'
```
**Cypher:**
```cypher
CREATE (u:Usuario {
    id: $id,
    nombre: $nombre,
    email: $email,
    edad: $edad,
    activo: $activo,
    fechaRegistro: date()
})
RETURN u
```

### 3.2 Crear nodo con 2+ labels (Actor:Director)
**Rúbrica:** CREATE/MERGE con 2+ labels

```bash
curl -X POST http://localhost:8000/actores \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Pedro Almodóvar",
    "nacionalidad": "Española",
    "fechaNacimiento": "1949-09-25",
    "premios": 12,
    "activo": true,
    "popularidad": 9.2,
    "papeles": ["Drama", "Comedia"],
    "es_director": true
  }'
```
**Cypher:**
```cypher
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
RETURN a
```

### 3.2b Agregar label :Director a actor existente
```bash
curl -X PATCH http://localhost:8000/actores/act_0344/agregar-director
```
**Cypher:**
```cypher
MATCH (a:Actor {id: $id})
SET a:Director
RETURN a
```

### 3.3 Crear nodo Serie con 9 propiedades
**Rúbrica:** Crear nodo con 5+ propiedades configuradas

```bash
curl -X POST http://localhost:8000/series \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Serie Prueba",
    "sinopsis": "Una serie de prueba para la presentación",
    "anio": 2024,
    "calificacion": 8.5,
    "numTemporadas": 3,
    "numEpisodios": 30,
    "estadoEmision": true,
    "activa": true
  }'
```
**Cypher:**
```cypher
CREATE (s:Serie {
    id: $id,
    titulo: $titulo,
    sinopsis: $sinopsis,
    anio: $anio,
    calificacion: $calificacion,
    numTemporadas: $numTemporadas,
    numEpisodios: $numEpisodios,
    estadoEmision: $estadoEmision,
    activa: $activa
})
RETURN s
```

---

## 4. VISUALIZACIÓN DE NODOS

### 4.1 Consultar 1 nodo
```bash
curl http://localhost:8000/series/ser_0864
curl http://localhost:8000/usuarios/usr_0655
```
**Cypher:**
```cypher
MATCH (s:Serie {id: $id})
OPTIONAL MATCH (s)-[:PERTENECE_A]->(g:Genero)
OPTIONAL MATCH (p:Plataforma)-[:TRANSMITE]->(s)
...
RETURN s, collect(DISTINCT ...) AS generos, ...
```

### 4.2 Consultar muchos nodos con filtros
```bash
curl "http://localhost:8000/series?calificacion_min=8.5&genero=Drama&limit=10"
curl "http://localhost:8000/usuarios?activo=true&edad_min=18&edad_max=30&limit=20"
```
**Cypher (series con filtros):**
```cypher
MATCH (s:Serie)
WHERE s.calificacion >= $calificacion_min
  AND EXISTS { MATCH (s)-[:PERTENECE_A]->(g3:Genero {nombre: $genero}) }
WITH s ORDER BY s.calificacion DESC SKIP $skip LIMIT $limit
OPTIONAL MATCH (s)-[:PERTENECE_A]->(g:Genero)
OPTIONAL MATCH (p:Plataforma)-[:TRANSMITE]->(s)
RETURN s, collect(DISTINCT g.nombre) AS generos, collect(DISTINCT p.nombre) AS plataformas
```

### 4.3 Consultas con agregaciones
```bash
curl "http://localhost:8000/series?genero=Drama"
```
**Cypher (agregaciones):**
```cypher
MATCH (s:Serie)
WHERE EXISTS { MATCH (s)-[:PERTENECE_A]->(g3:Genero {nombre: $genero}) }
OPTIONAL MATCH (s)-[:PERTENECE_A]->(g:Genero)
OPTIONAL MATCH (p:Plataforma)-[:TRANSMITE]->(s)
RETURN
    count(DISTINCT s) AS total,
    avg(s.calificacion) AS promedio_calificacion,
    collect(DISTINCT g.nombre) AS generos_list,
    collect(DISTINCT p.nombre) AS plataformas_list
```

---

## 5. GESTIÓN DE PROPIEDADES DE NODOS

### 5.1 Agregar/actualizar propiedades de 1 nodo
```bash
curl -X PATCH http://localhost:8000/series/ser_0864 \
  -H "Content-Type: application/json" \
  -d '{"propiedades": {"calificacion": 9.1, "destacada": true}}'

curl -X PATCH http://localhost:8000/usuarios/usr_0655 \
  -H "Content-Type: application/json" \
  -d '{"propiedades": {"edad": 30}}'
```
**Cypher:**
```cypher
MATCH (s:Serie {id: $id})
SET s += $propiedades
RETURN s
```

### 5.2 Agregar/actualizar propiedades de múltiples nodos
```bash
curl -X PATCH http://localhost:8000/series/masivo \
  -H "Content-Type: application/json" \
  -d '{
    "ids": ["ser_0864", "ser_1526", "ser_2511"],
    "propiedades": {"destacada": true, "calificacion": 9.0}
  }'
```
**Cypher:**
```cypher
UNWIND $ids AS serie_id
MATCH (s:Serie {id: serie_id})
SET s += $propiedades
RETURN count(s) AS actualizadas
```

### 5.3 Eliminar propiedades de 1 nodo
```bash
curl -X DELETE http://localhost:8000/series/ser_0864/propiedades \
  -H "Content-Type: application/json" \
  -d '{"nombres": ["destacada"]}'
```
**Cypher:**
```cypher
MATCH (s:Serie {id: $id})
REMOVE s.`destacada`
RETURN s
```

### 5.4 Eliminar propiedades de múltiples nodos
```bash
curl -X DELETE http://localhost:8000/series/masivo/propiedades \
  -H "Content-Type: application/json" \
  -d '{"ids": ["ser_0864", "ser_1526"], "nombres": ["destacada", "temporal"]}'
```
**Cypher:**
```cypher
UNWIND $ids AS serie_id
MATCH (s:Serie {id: serie_id})
REMOVE s.`destacada`, s.`temporal`
RETURN count(s) AS afectadas
```

---

## 6. RELACIONES CON PROPIEDADES

### 6.1 Crear relación con propiedades (3+)
```bash
# VIO — 3 propiedades + fecha auto
curl -X POST "http://localhost:8000/usuarios/usr_0655/vio/ser_0864" \
  -H "Content-Type: application/json" \
  -d '{"porcentajeVisto": 75.5, "completada": false, "calificacion": 8.0}'

# PERTENECE_A — 3 propiedades
curl -X POST "http://localhost:8000/relaciones/pertenece-a/ser_0864/gen_020" \
  -H "Content-Type: application/json" \
  -d '{"esPrincipal": true, "relevancia": 0.9, "fechaAsignacion": "2024-01-15"}'

# SIGUE_A — flag mutuo automático
curl -X POST "http://localhost:8000/usuarios/usr_0037/sigue/usr_0386" \
  -H "Content-Type: application/json" \
  -d '{"notificaciones": true}'
```
**Cypher (VIO):**
```cypher
MATCH (u:Usuario {id: $usuario_id})
MATCH (s:Serie {id: $serie_id})
MERGE (u)-[r:VIO]->(s)
ON CREATE SET r.fecha = date()
SET r += $props
RETURN r
```

### 6.2 Actualizar propiedades de 1 relación
```bash
curl -X PATCH "http://localhost:8000/usuarios/usr_0655/vio/ser_0864" \
  -H "Content-Type: application/json" \
  -d '{"porcentajeVisto": 100.0, "completada": true}'
```
**Cypher:**
```cypher
MATCH (u:Usuario {id: $usuario_id})-[r:VIO]->(s:Serie {id: $serie_id})
SET r += $props
RETURN r
```

### 6.3 Actualizar propiedades de múltiples relaciones
```bash
curl -X PATCH "http://localhost:8000/usuarios/usr_0655/vio/masivo" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"serie_id": "ser_0864", "completada": true, "porcentajeVisto": 100.0},
      {"serie_id": "ser_1526", "completada": false, "porcentajeVisto": 40.0}
    ]
  }'
```
**Cypher:**
```cypher
UNWIND $items AS item
MATCH (u:Usuario {id: $usuario_id})-[r:VIO]->(s:Serie {id: item.serie_id})
SET r += item.props
RETURN count(r) AS afectados
```

### 6.4 Eliminar propiedades de 1 relación
```bash
curl -X DELETE "http://localhost:8000/usuarios/usr_0655/vio/ser_1168/propiedades" \
  -H "Content-Type: application/json" \
  -d '{"nombres": ["calificacion"]}'
```
**Cypher:**
```cypher
MATCH (u:Usuario {id: $usuario_id})-[r:VIO]->(s:Serie {id: $serie_id})
REMOVE r.`calificacion`
RETURN r
```

### 6.5 Eliminar propiedades de múltiples relaciones
```bash
curl -X DELETE "http://localhost:8000/usuarios/usr_0655/vio/masivo/propiedades" \
  -H "Content-Type: application/json" \
  -d '{"serie_ids": ["ser_2627", "ser_1326"], "nombres": ["calificacion"]}'
```
**Cypher:**
```cypher
MATCH (u:Usuario {id: $usuario_id})-[r:VIO]->(s:Serie)
WHERE s.id IN $serie_ids
REMOVE r.`calificacion`
RETURN count(r) AS afectadas
```

---

## 7. ELIMINAR NODOS

### 7.1 Eliminar 1 nodo
```bash
curl -X DELETE http://localhost:8000/series/ser_0015
curl -X DELETE http://localhost:8000/usuarios/usr_0386
```
**Cypher:**
```cypher
MATCH (s:Serie {id: $id})
DETACH DELETE s
RETURN count(s) AS eliminadas
```

### 7.2 Eliminar múltiples nodos
```bash
curl -X DELETE http://localhost:8000/series/masivo \
  -H "Content-Type: application/json" \
  -d '{"ids": ["ser_0015", "ser_1526"]}'
```
**Cypher:**
```cypher
UNWIND $ids AS serie_id
MATCH (s:Serie {id: serie_id})
DETACH DELETE s
RETURN count(s) AS eliminadas
```

---

## 8. ELIMINAR RELACIONES

### 8.1 Eliminar 1 relación
```bash
curl -X DELETE "http://localhost:8000/usuarios/usr_0655/vio/ser_0864"
curl -X DELETE "http://localhost:8000/usuarios/usr_0037/sigue/usr_0386"
curl -X DELETE "http://localhost:8000/relaciones/pertenece-a/ser_0864/gen_020"
```
**Cypher:**
```cypher
MATCH (u:Usuario {id: $usuario_id})-[r:VIO]->(s:Serie {id: $serie_id})
DELETE r
RETURN count(r) AS eliminadas
```

### 8.2 Eliminar múltiples relaciones
```bash
curl -X DELETE "http://localhost:8000/usuarios/usr_0655/le-gusta/masivo" \
  -H "Content-Type: application/json" \
  -d '{"serie_ids": ["ser_0864", "ser_1526", "ser_2511"]}'
```
**Cypher:**
```cypher
MATCH (u:Usuario {id: $usuario_id})-[r:LE_GUSTA]->(s:Serie)
WHERE s.id IN $serie_ids
WITH collect(r) AS rels
FOREACH (r IN rels | DELETE r)
RETURN size(rels) AS afectados
```

---

## 9. CONSULTAS CYPHER — PRESENTACIÓN (2 por persona)

### PERSONA 1

#### Query P1-A: Top series por género (agregación avanzada)
```bash
curl http://localhost:8000/consultas/series-mejor-calificadas-por-genero
```
**Cypher:**
```cypher
MATCH (s:Serie)-[:PERTENECE_A]->(g:Genero)
WITH g, s ORDER BY s.calificacion DESC
WITH g,
     collect(s)[0..5] AS top_series,
     avg(s.calificacion) AS promedio_calificacion,
     count(s) AS cantidad_series
ORDER BY promedio_calificacion DESC
RETURN
    g.id AS genero_id,
    g.nombre AS genero,
    [ts IN top_series | {id: ts.id, titulo: ts.titulo, calificacion: ts.calificacion}] AS top_series,
    promedio_calificacion,
    cantidad_series
```
**Resultado clave:** Variedades lidera con promedio 7.19 sobre 119 series. Ordenamiento doble (serie interna + género externo).

#### Query P1-B: Plataformas más exclusivas (COUNT condicional)
```bash
curl http://localhost:8000/consultas/plataformas-mas-exclusivas
```
**Cypher:**
```cypher
MATCH (p:Plataforma)-[r:TRANSMITE]->(s:Serie)
WITH p,
     count(s) AS total_series,
     count(CASE WHEN r.exclusiva = true THEN 1 END) AS total_exclusivas
WHERE total_series > 0
WITH p, total_series, total_exclusivas,
     round(100.0 * total_exclusivas / total_series, 2) AS porcentaje_exclusivas
ORDER BY porcentaje_exclusivas DESC, total_exclusivas DESC
RETURN p.id, p.nombre, total_exclusivas, total_series, porcentaje_exclusivas
```
**Resultado clave:** Peacock 55.74% (102/183). Netflix 50.98% (104/204). Rango comprimido 44-56%.

---

### PERSONA 2

#### Query P2-A: Recomendaciones colaborativas (traversal social)
```bash
curl "http://localhost:8000/recomendaciones/usr_0655?limit=8"
```
**Cypher:**
```cypher
MATCH (u:Usuario {id: $usuario_id})
OPTIONAL MATCH (u)-[:LE_GUSTA|VIO]->(:Serie)<-[:LE_GUSTA]-(afin:Usuario)
OPTIONAL MATCH (u)-[:SIGUE_A]->(seguido:Usuario)
WITH u, collect(DISTINCT afin) + collect(DISTINCT seguido) AS otros
UNWIND otros AS otro
WITH u, otro WHERE otro IS NOT NULL AND otro.id <> u.id
MATCH (otro)-[:LE_GUSTA]->(rec:Serie)
WHERE NOT (u)-[:VIO]->(rec)
  AND NOT (u)-[:LE_GUSTA]->(rec)
  AND NOT (u)-[:EN_LISTA]->(rec)
WITH rec,
     count(DISTINCT otro) AS usuarios_similares,
     collect(DISTINCT otro.nombre)[0..5] AS muestra_usuarios
RETURN rec.id, rec.titulo, usuarios_similares, muestra_usuarios
ORDER BY usuarios_similares DESC LIMIT $limit
```
**Resultado clave:** "The Last of Us" y "The Bear Heist" aparecen. `usuario_0214` es el vecino más influyente (aparece en 3 recomendaciones distintas).

#### Query P2-B: Usuarios influyentes (score compuesto sobre grafo social)
```bash
curl "http://localhost:8000/consultas/usuarios-influyentes?limit=10"
```
**Cypher:**
```cypher
MATCH (u:Usuario)
OPTIONAL MATCH (u)<-[:SIGUE_A]-(seguidor:Usuario)
OPTIONAL MATCH (u)-[:ESCRIBIO]->(r:Resena)
WITH u,
     count(DISTINCT seguidor) AS seguidores,
     count(DISTINCT r) AS resenas
RETURN u.id, u.nombre, seguidores, resenas,
       (seguidores * 2 + resenas) AS influencia
ORDER BY influencia DESC, seguidores DESC
LIMIT $limit
```
**Resultado clave:** `usr_0655` lidera con 28 pts (11 seg + 6 res). El peso 2× de seguidores es intencional: el reach supera a las reseñas.

---

### PERSONA 3

#### Query P3-A: Jaccard Similarity — EXTRA DATA SCIENCE (10 pts)
```bash
curl "http://localhost:8000/recomendaciones/usr_0655/avanzado?limit=8"
```
**Cypher (simplificado):**
```cypher
MATCH (u:Usuario {id: $usuario_id})
OPTIONAL MATCH (u)-[:LE_GUSTA|VIO]->(s_u:Serie)
WITH u, collect(DISTINCT s_u) AS likes_u

MATCH (rec:Serie)
WHERE NOT (u)-[:VIO]->(rec) AND NOT (u)-[:LE_GUSTA]->(rec)

OPTIONAL MATCH (otro:Usuario)-[:LE_GUSTA|VIO]->(rec) WHERE otro <> u
OPTIONAL MATCH (otro)-[:LE_GUSTA|VIO]->(s_o:Serie)
WITH u, likes_u, rec, otro, collect(DISTINCT s_o) AS likes_otro,
     [s IN likes_otro WHERE s IN likes_u] AS interseccion

WITH ... CASE WHEN size(likes_u)=0 OR size(likes_otro)=0 THEN 0.0
              ELSE toFloat(size(interseccion))/(size(likes_u)+size(likes_otro)-size(interseccion))
         END AS jaccard_uo

-- Score final ponderado:
($w_jaccard * score_jaccard) +
($w_genero  * toFloat(bonus_genero)) +
($w_social  * toFloat(bonus_social)) +
($w_pop     * log(popularidad + 1)) +
($w_novedad * CASE WHEN rec.anio >= date().year THEN 1.0
                   ELSE exp(-toFloat(date().year - rec.anio) / 5.0) END)
AS score
```
**Resultado clave:** "Beyond Materials" score 2.368 (Jaccard 0.048 + genero 3 + social 1 + novedad 0.67). Score completamente explicable componente a componente.

#### Query P3-B: Actores con multi-label :Actor:Director
```bash
curl "http://localhost:8000/consultas/actores-que-tambien-dirigen?limit=10"
```
**Cypher:**
```cypher
MATCH (a:Actor:Director)
OPTIONAL MATCH (a)-[:ACTUA_EN]->(serie_act:Serie)
OPTIONAL MATCH (a)-[:DIRIGE]->(serie_dir:Serie)
WITH a,
     count(DISTINCT serie_act) AS series_actuadas,
     count(DISTINCT serie_dir) AS series_dirigidas,
     collect(DISTINCT serie_dir.titulo)[0..5] AS muestra_dirigidas
RETURN a.id, a.nombre, a.nacionalidad,
       series_actuadas, series_dirigidas,
       (series_actuadas + series_dirigidas) AS total,
       muestra_dirigidas
ORDER BY total DESC, series_dirigidas DESC
LIMIT $limit
```
**Resultado clave:** Zazie Stiller lidera (33 act + 3 dir = 36). `MATCH (a:Actor:Director)` es el patrón que demuestra multi-label en consulta.

---

## 10. ANÁLISIS DE DATOS — INTERPRETACIÓN

### Distribución de géneros
- 40+ géneros con 100-130 series cada uno → distribución uniforme (datos sintéticos bien generados)
- Ningún género supera promedio 7.5 → calificaciones realistas distribuidas

### Competencia entre plataformas
- Peacock (55.74%) supera a Netflix (50.98%) en exclusividad porcentual
- Disney+ (48.39%) es el menos exclusivo del top — lógico dado su catálogo familiar amplio
- Rango 44-56%: todas las plataformas compiten de forma pareja

### Red social de usuarios
- Score máximo de influencia: 28 pts → red relativamente esparsa
- El peso 2× en seguidores vs reseñas hace que `usr_0037` (13 seg, 1 res = 27) supere a `usr_0386` (11 seg, 4 res = 26)
- `usuario_0214` es hub natural del grafo: aparece como vecino común en 3 recomendaciones para usr_0655

### Motor de recomendaciones
- Jaccard score bajo (0.028-0.087) indica que la red de likes es esparsa — típico en sistemas reales al inicio
- El bonus de género (3 géneros coincidentes) es el signal más fuerte actualmente
- `novedad` varía entre 0.007 y 0.67 → la decaída exponencial exp(-años/5) distribuye bien series antiguas vs recientes
- Series con `anio >= 2026` reciben novedad=1.0 (score máximo de frescura)
