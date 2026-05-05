import { useState, useEffect } from 'react'
import { api, toList } from '../../api'
import { Btn, Card, Badge, Spinner, Empty, Alert, FG, Modal, ModalFooter, PageHeader, toast } from '../../components/ui'

/* ═══════════════════════════════════════
   ACTORES
═══════════════════════════════════════ */
export function AdminActores() {
  const [actores, setActores] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState({})
  const [selected, setSelected] = useState(null)
  const [busqueda, setBusqueda] = useState('')

  const load = async () => {
    setLoading(true); setError(null)
    try { const d = await api('GET', '/actores'); setActores(toList(d, ['actores', 'data'])) }
    catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [])

  const ff = (k) => (e) => setForm(p => ({ ...p, [k]: e.target.value }))

  const crear = async () => {
    if (!form.nombre || !form.nacionalidad || !form.fechaNacimiento || !form.popularidad) {
      toast('Nombre, nacionalidad, fecha de nacimiento y popularidad son requeridos', 'error'); return
    }
    try {
      await api('POST', '/actores', {
        nombre: form.nombre,
        nacionalidad: form.nacionalidad,
        fechaNacimiento: form.fechaNacimiento,
        premios: parseInt(form.premios) || 0,
        activo: true,
        popularidad: parseFloat(form.popularidad) || 0,
        papeles: (form.papeles || '').split(',').map(x => x.trim()).filter(Boolean),
        es_director: form.esDirector === true,
      })
      toast('Actor creado', 'success'); setModal(null); setForm({}); load()
    } catch (e) { toast(e.message, 'error') }
  }

  const agregarDir = async (id) => {
    try { await api('PATCH', `/actores/${id}/agregar-director`); toast('Label :Director agregado', 'success'); setModal(null); load() }
    catch (e) { toast(e.message, 'error') }
  }

  const vincular = async () => {
    if (!form.serieId || !form.personaje) { toast('ID de serie y personaje son requeridos', 'error'); return }
    try {
      await api('POST', `/actores/${selected.id}/actua-en/${form.serieId}`, {
        personaje: form.personaje,
        protagonista: form.protagonista === true,
        temporadas: (form.temporadas || '').split(',').map(x => parseInt(x.trim())).filter(n => !isNaN(n)),
      })
      toast('Vínculo creado', 'success'); setModal(null); setForm({})
    } catch (e) { toast(e.message, 'error') }
  }

  const actualizarVinculo = async () => {
    if (!form.serieId) { toast('ID de serie requerido', 'error'); return }
    const body = {}
    if (form.personaje) body.personaje = form.personaje
    if (form.protagonista !== undefined) body.protagonista = form.protagonista === true
    if (form.temporadas) body.temporadas = form.temporadas.split(',').map(x => parseInt(x.trim())).filter(n => !isNaN(n))
    try {
      await api('PATCH', `/actores/${selected.id}/actua-en/${form.serieId}`, body)
      toast('Vínculo actualizado', 'success'); setModal(null); setForm({})
    } catch (e) { toast(e.message, 'error') }
  }

  const eliminarVinculo = async () => {
    if (!form.serieId) { toast('ID de serie requerido', 'error'); return }
    try {
      await api('DELETE', `/actores/${selected.id}/actua-en/${form.serieId}`)
      toast('Vínculo eliminado', 'success'); setModal(null); setForm({})
    } catch (e) { toast(e.message, 'error') }
  }

  const esDirector = (a) => Array.isArray(a.labels) && a.labels.includes('Director')

  const actoresFiltrados = busqueda.trim()
    ? actores.filter(a => {
        const q = busqueda.toLowerCase()
        return (a.nombre || '').toLowerCase().includes(q)
            || (a.nacionalidad || '').toLowerCase().includes(q)
      })
    : actores

  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <PageHeader
        title="Actores"
        subtitle="Gestión de actores y directores. Los nodos pueden tener múltiples labels."
        action={<Btn onClick={() => { setForm({}); setModal('crear') }}>+ Nuevo actor</Btn>}
      />
      <div style={{ marginBottom: 16, maxWidth: 320 }}>
        <input
          value={busqueda}
          onChange={e => setBusqueda(e.target.value)}
          placeholder="Buscar por nombre o nacionalidad…"
          style={{ width: '100%' }}
        />
      </div>
      {loading && <Spinner />}
      {error && <Alert type="error">{error}</Alert>}
      {!loading && !error && actoresFiltrados.length === 0 && <Empty message={busqueda ? `Sin resultados para "${busqueda}"` : 'Sin actores registrados'} icon="◎" />}
      {!loading && !error && actoresFiltrados.length > 0 && (
        <Card style={{ overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead style={{ background: 'var(--off)' }}>
              <tr>{['Nombre','Labels','Nacionalidad','F. Nacimiento',''].map(h => (
                <th key={h} style={{ padding: '10px 16px', textAlign: 'left', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text-xs)', borderBottom: '1.5px solid var(--border)' }}>{h}</th>
              ))}</tr>
            </thead>
            <tbody>
              {actoresFiltrados.map(a => (
                <tr key={a.id} style={{ borderBottom: '1px solid var(--border)' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--off)'}
                  onMouseLeave={e => e.currentTarget.style.background = ''}>
                  <td style={{ padding: '12px 16px', fontWeight: 600 }}>{a.nombre || '-'}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', gap: 5 }}>
                      <Badge color="gray">Actor</Badge>
                      {esDirector(a) && <Badge color="blue">Director</Badge>}
                    </div>
                  </td>
                  <td style={{ padding: '12px 16px', color: 'var(--text-xs)' }}>{a.nacionalidad || '-'}</td>
                  <td style={{ padding: '12px 16px', color: 'var(--text-xs)' }}>{a.fechaNacimiento || '-'}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                      {!esDirector(a) && (
                        <Btn size="sm" variant="ghost" onClick={() => { setSelected(a); setModal('agregarDir') }}>+ Director</Btn>
                      )}
                      <Btn size="sm" variant="ghost" onClick={() => { setSelected(a); setForm({}); setModal('vincular') }}>+ Vínculo</Btn>
                      <Btn size="sm" variant="ghost" onClick={() => { setSelected(a); setForm({}); setModal('editarVinculo') }}>Editar vínculo</Btn>
                      <Btn size="sm" variant="danger" onClick={() => { setSelected(a); setForm({}); setModal('eliminarVinculo') }}>- Vínculo</Btn>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}

      {/* Modal: Crear actor */}
      {modal === 'crear' && (
        <Modal title="Nuevo actor" onClose={() => setModal(null)}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <FG label="Nombre *"><input value={form.nombre || ''} onChange={ff('nombre')} /></FG>
            <FG label="Nacionalidad *"><input value={form.nacionalidad || ''} onChange={ff('nacionalidad')} /></FG>
            <FG label="F. nacimiento *"><input type="date" value={form.fechaNacimiento || ''} onChange={ff('fechaNacimiento')} /></FG>
            <FG label="Popularidad * (0-100)"><input type="number" min="0" max="100" step="0.1" value={form.popularidad || ''} onChange={ff('popularidad')} /></FG>
            <FG label="Premios (número)"><input type="number" min="0" value={form.premios || ''} onChange={ff('premios')} placeholder="0" /></FG>
            <FG label="Papeles (coma)"><input value={form.papeles || ''} onChange={ff('papeles')} placeholder="Protagonista, Villano…" /></FG>
          </div>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', marginTop: 4, marginBottom: 0, textTransform: 'none', letterSpacing: 0, fontSize: 13.5 }}>
            <input type="checkbox" checked={form.esDirector || false} onChange={e => setForm(p => ({ ...p, esDirector: e.target.checked }))} style={{ width: 'auto' }} />
            También es Director <Badge color="blue">Multi-label</Badge>
          </label>
          <ModalFooter>
            <Btn variant="outline" onClick={() => setModal(null)}>Cancelar</Btn>
            <Btn onClick={crear}>Crear actor</Btn>
          </ModalFooter>
        </Modal>
      )}

      {/* Modal: Agregar label Director */}
      {modal === 'agregarDir' && selected && (
        <Modal title="Agregar label Director" onClose={() => setModal(null)}>
          <p style={{ fontSize: 13.5, color: 'var(--text-xs)', marginBottom: 20, lineHeight: 1.6 }}>
            Se añadirá el label <Badge color="blue">:Director</Badge> al actor <strong>{selected.nombre}</strong>.
            El nodo tendrá dos labels: <code style={{ background: 'var(--g100)', padding: '2px 6px', borderRadius: 4 }}>:Actor :Director</code>
          </p>
          <ModalFooter>
            <Btn variant="outline" onClick={() => setModal(null)}>Cancelar</Btn>
            <Btn onClick={() => agregarDir(selected.id)}>Confirmar</Btn>
          </ModalFooter>
        </Modal>
      )}

      {/* Modal: Crear vínculo ACTUA_EN */}
      {modal === 'vincular' && selected && (
        <Modal title={`Nuevo vínculo — ${selected.nombre}`} onClose={() => setModal(null)}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <FG label="ID de la serie *"><input value={form.serieId || ''} onChange={ff('serieId')} placeholder="ser_0001" /></FG>
            <FG label="Personaje *"><input value={form.personaje || ''} onChange={ff('personaje')} placeholder="Nombre del personaje" /></FG>
            <FG label="Temporadas (coma)"><input value={form.temporadas || ''} onChange={ff('temporadas')} placeholder="1,2,3" /></FG>
          </div>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', marginTop: 4, marginBottom: 0, textTransform: 'none', letterSpacing: 0, fontSize: 13.5 }}>
            <input type="checkbox" checked={form.protagonista || false} onChange={e => setForm(p => ({ ...p, protagonista: e.target.checked }))} style={{ width: 'auto' }} />
            Protagonista
          </label>
          <ModalFooter>
            <Btn variant="outline" onClick={() => setModal(null)}>Cancelar</Btn>
            <Btn onClick={vincular}>Crear vínculo</Btn>
          </ModalFooter>
        </Modal>
      )}

      {/* Modal: Editar vínculo ACTUA_EN */}
      {modal === 'editarVinculo' && selected && (
        <Modal title={`Editar vínculo — ${selected.nombre}`} onClose={() => setModal(null)}>
          <p style={{ fontSize: 12.5, color: 'var(--text-xs)', marginBottom: 14 }}>Solo los campos que completes se actualizarán.</p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <FG label="ID de la serie *"><input value={form.serieId || ''} onChange={ff('serieId')} placeholder="ser_0001" /></FG>
            <FG label="Personaje"><input value={form.personaje || ''} onChange={ff('personaje')} placeholder="Nombre del personaje" /></FG>
            <FG label="Temporadas (coma)"><input value={form.temporadas || ''} onChange={ff('temporadas')} placeholder="1,2,3" /></FG>
          </div>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', marginTop: 4, marginBottom: 0, textTransform: 'none', letterSpacing: 0, fontSize: 13.5 }}>
            <input type="checkbox" checked={form.protagonista || false} onChange={e => setForm(p => ({ ...p, protagonista: e.target.checked }))} style={{ width: 'auto' }} />
            Protagonista
          </label>
          <ModalFooter>
            <Btn variant="outline" onClick={() => setModal(null)}>Cancelar</Btn>
            <Btn onClick={actualizarVinculo}>Actualizar</Btn>
          </ModalFooter>
        </Modal>
      )}

      {/* Modal: Eliminar vínculo ACTUA_EN */}
      {modal === 'eliminarVinculo' && selected && (
        <Modal title={`Eliminar vínculo — ${selected.nombre}`} onClose={() => setModal(null)}>
          <FG label="ID de la serie *">
            <input value={form.serieId || ''} onChange={ff('serieId')} placeholder="ser_0001" />
          </FG>
          <p style={{ fontSize: 12.5, color: 'var(--text-xs)', marginTop: 8 }}>
            Se eliminará la relación ACTUA_EN entre <strong>{selected.nombre}</strong> y la serie indicada.
          </p>
          <ModalFooter>
            <Btn variant="outline" onClick={() => setModal(null)}>Cancelar</Btn>
            <Btn variant="danger" onClick={eliminarVinculo}>Eliminar vínculo</Btn>
          </ModalFooter>
        </Modal>
      )}
    </div>
  )
}

/* ═══════════════════════════════════════
   CSV
═══════════════════════════════════════ */
const TIPO_OPTS = [
  { group: 'Nodos', items: [
    { value: 'series',     label: 'Series' },
    { value: 'actores',    label: 'Actores / Directores' },
    { value: 'usuarios',   label: 'Usuarios' },
    { value: 'generos',    label: 'Géneros' },
    { value: 'plataformas',label: 'Plataformas' },
    { value: 'estudios',   label: 'Estudios de producción' },
    { value: 'resenas',    label: 'Reseñas' },
  ]},
  { group: 'Relaciones', items: [
    { value: 'pertenece_a', label: 'Serie → Género' },
    { value: 'transmite',   label: 'Plataforma → Serie' },
    { value: 'actua_en',    label: 'Actor actúa en Serie' },
    { value: 'dirige',      label: 'Director dirige Serie' },
    { value: 'produjo',     label: 'Estudio produjo Serie' },
    { value: 'vio',         label: 'Usuario vio Serie' },
    { value: 'le_gusta',    label: 'Usuario le gusta Serie' },
    { value: 'en_lista',    label: 'Usuario en lista Serie' },
    { value: 'sigue_a',     label: 'Usuario sigue a Usuario' },
    { value: 'similar_a',   label: 'Serie similar a Serie' },
    { value: 'escribio',    label: 'Usuario escribió Reseña' },
    { value: 'sobre',       label: 'Reseña sobre Serie' },
  ]},
]

export function AdminCSV() {
  const [completo, setCompleto] = useState({ loading: false, result: null })
  const [subida, setSubida] = useState({ tipo: 'series', file: null, loading: false, result: null })

  const cargarTodo = async () => {
    setCompleto({ loading: true, result: null })
    try {
      const data = await api('POST', '/admin/cargar-csv')
      setCompleto({ loading: false, result: { ok: true, msg: `${data.mensaje} — ${data.total_nodos} nodos, ${data.total_relaciones} relaciones` } })
    } catch (e) { setCompleto({ loading: false, result: { ok: false, msg: e.message } }) }
  }

  const subirArchivo = async () => {
    if (!subida.file) { toast('Selecciona un archivo CSV', 'error'); return }
    setSubida(p => ({ ...p, loading: true, result: null }))
    const fd = new FormData()
    fd.append('tipo', subida.tipo)
    fd.append('file', subida.file)
    try {
      const r = await fetch('http://localhost:8000/admin/subir-csv', { method: 'POST', body: fd })
      if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.statusText)
      const data = await r.json()
      setSubida(p => ({ ...p, loading: false, result: { ok: true, msg: data.mensaje } }))
    } catch (e) { setSubida(p => ({ ...p, loading: false, result: { ok: false, msg: e.message } })) }
  }

  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <PageHeader title="Carga de datos CSV" subtitle="Carga completa desde data/ o sube un CSV para agregar y actualizar registros." />
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, maxWidth: 900 }}>

        {/* Sección 1: carga completa */}
        <Card style={{ padding: '26px 28px' }}>
          <div style={{ fontFamily: 'Syne,sans-serif', fontWeight: 700, fontSize: 16, marginBottom: 6 }}>Carga completa</div>
          <div style={{ fontSize: 13, color: 'var(--text-xs)', marginBottom: 20, lineHeight: 1.6 }}>
            Lee todos los archivos de <code style={{ background: 'var(--g100)', padding: '1px 5px', borderRadius: 4 }}>data/</code> y hace MERGE de nodos y relaciones en Neo4j.
          </div>
          <Btn onClick={cargarTodo} disabled={completo.loading}>
            {completo.loading ? 'Cargando…' : '↺ Cargar todos los CSVs'}
          </Btn>
          {completo.result && (
            <div style={{ marginTop: 14 }}>
              <Alert type={completo.result.ok ? 'success' : 'error'}>
                {completo.result.ok ? '✓ ' : '✗ '}{completo.result.msg}
              </Alert>
            </div>
          )}
        </Card>

        {/* Sección 2: subir archivo */}
        <Card style={{ padding: '26px 28px' }}>
          <div style={{ fontFamily: 'Syne,sans-serif', fontWeight: 700, fontSize: 16, marginBottom: 6 }}>Agregar registros</div>
          <div style={{ fontSize: 13, color: 'var(--text-xs)', marginBottom: 20, lineHeight: 1.6 }}>
            Sube un CSV con encabezados para insertar o actualizar registros de una entidad o relación específica.
          </div>
          <FG label="Tipo de entidad / relación">
            <select value={subida.tipo} onChange={e => setSubida(p => ({ ...p, tipo: e.target.value }))}>
              {TIPO_OPTS.map(({ group, items }) => (
                <optgroup key={group} label={group}>
                  {items.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                </optgroup>
              ))}
            </select>
          </FG>
          <FG label="Archivo CSV">
            <input type="file" accept=".csv" onChange={e => setSubida(p => ({ ...p, file: e.target.files[0] }))}
              style={{ padding: '8px', cursor: 'pointer', fontSize: 13 }} />
          </FG>
          {subida.file && <div style={{ fontSize: 12, color: 'var(--text-xs)', marginBottom: 10 }}>{subida.file.name}</div>}
          <Btn onClick={subirArchivo} disabled={subida.loading}>
            {subida.loading ? 'Procesando…' : '↑ Subir y cargar'}
          </Btn>
          {subida.result && (
            <div style={{ marginTop: 14 }}>
              <Alert type={subida.result.ok ? 'success' : 'error'}>
                {subida.result.ok ? '✓ ' : '✗ '}{subida.result.msg}
              </Alert>
            </div>
          )}
        </Card>

      </div>
    </div>
  )
}

/* ═══════════════════════════════════════
   CONSULTAS CYPHER
═══════════════════════════════════════ */
const QUERIES = [
  { id: 'top-series',      label: 'Top series',            desc: 'Mejor calificadas, filtro opcional por género', path: '/consultas/top-series',                          hasGenero: true },
  { id: 'por-genero',      label: 'Series por género',     desc: 'Top 5 por cada género, ordenado por promedio',  path: '/consultas/series-mejor-calificadas-por-genero' },
  { id: 'plataformas',     label: 'Plataformas exclusivas',desc: '% de contenido exclusivo por plataforma',       path: '/consultas/plataformas-mas-exclusivas' },
  { id: 'influyentes',     label: 'Usuarios influyentes',  desc: 'Mayor impacto en la red social',                path: '/consultas/usuarios-influyentes',                hasLimit: true },
  { id: 'top-actores',     label: 'Top actores',           desc: 'Por series en las que participan',              path: '/consultas/top-actores',                         hasLimit: true },
  { id: 'actor-director',  label: 'Actor + Director',      desc: 'Nodos con multi-label :Actor:Director',         path: '/consultas/actores-que-tambien-dirigen',         hasLimit: true },
]

function cellVal(v) {
  if (Array.isArray(v)) return v.map(x => (x && typeof x === 'object') ? (x.titulo || JSON.stringify(x)) : x).join(', ') || '—'
  if (typeof v === 'number') return Number.isInteger(v) ? v : v.toFixed(2)
  return String(v ?? '—')
}

export function AdminConsultas() {
  const [result, setResult] = useState(null)
  const [activeId, setActiveId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [genero, setGenero] = useState('')
  const [limit, setLimit] = useState('')

  const run = async (q) => {
    setActiveId(q.id); setLoading(true); setResult(null)
    try {
      const p = new URLSearchParams()
      if (q.hasGenero && genero) p.set('genero', genero)
      if (q.hasLimit && limit) p.set('limit', limit)
      const qs = p.toString()
      const data = await api('GET', `${q.path}${qs ? '?' + qs : ''}`)
      const list = Array.isArray(data) ? data : (data?.items ?? [])
      setResult({ label: q.label, list })
    } catch (e) { toast(e.message, 'error') }
    finally { setLoading(false) }
  }

  const active = QUERIES.find(q => q.id === activeId)
  const cols = result?.list[0] ? Object.keys(result.list[0]).slice(0, 6) : []

  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <PageHeader title="Consultas" subtitle="Análisis analítico sobre el grafo de series en Neo4j." />

      {/* filtros */}
      {active && (active.hasGenero || active.hasLimit) && (
        <Card style={{ padding: '14px 20px', marginBottom: 18, display: 'flex', gap: 12, alignItems: 'flex-end', flexWrap: 'wrap' }}>
          {active.hasGenero && (
            <FG label="Género">
              <input value={genero} onChange={e => setGenero(e.target.value)} placeholder="Drama, Thriller…" style={{ width: 160 }} />
            </FG>
          )}
          {active.hasLimit && (
            <FG label="Límite">
              <input type="number" value={limit} onChange={e => setLimit(e.target.value)} placeholder="10" style={{ width: 80 }} />
            </FG>
          )}
          <Btn onClick={() => run(active)}>↻ Aplicar filtros</Btn>
        </Card>
      )}

      {/* tarjetas */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12, marginBottom: 28 }}>
        {QUERIES.map(q => (
          <Card key={q.id} hover onClick={() => { setGenero(''); setLimit(''); run(q) }}
            style={{ padding: '20px 22px', cursor: 'pointer', border: activeId === q.id ? '1.5px solid var(--g400)' : undefined }}>
            <div style={{ fontFamily: 'Syne,sans-serif', fontWeight: 700, fontSize: 15, marginBottom: 5 }}>{q.label}</div>
            <div style={{ fontSize: 12.5, color: 'var(--text-xs)' }}>{q.desc}</div>
          </Card>
        ))}
      </div>

      {loading && <Spinner />}

      {result && result.list.length === 0 && <Alert type="info">Sin resultados para esta consulta.</Alert>}

      {result && result.list.length > 0 && (
        <Card style={{ overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1.5px solid var(--border)', fontFamily: 'Syne,sans-serif', fontWeight: 700, fontSize: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>{result.label}</span>
            <span style={{ fontSize: 12.5, fontWeight: 400, color: 'var(--text-xs)' }}>{result.list.length} resultados</span>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead style={{ background: 'var(--off)' }}>
              <tr>{cols.map(k => (
                <th key={k} style={{ padding: '10px 16px', textAlign: 'left', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text-xs)', borderBottom: '1.5px solid var(--border)' }}>
                  {k.replace(/_/g, ' ')}
                </th>
              ))}</tr>
            </thead>
            <tbody>
              {result.list.map((row, i) => (
                <tr key={i} style={{ borderBottom: '1px solid var(--border)' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--off)'}
                  onMouseLeave={e => e.currentTarget.style.background = ''}>
                  {cols.map((k, j) => (
                    <td key={k} style={{ padding: '11px 16px', fontSize: 13.5, color: j === 0 ? 'var(--text)' : 'var(--text-sm)', fontWeight: j === 0 ? 600 : 400, maxWidth: 260, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {cellVal(row[k])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  )
}
