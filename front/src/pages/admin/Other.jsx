import { useState, useEffect } from 'react'
import { api, toList } from '../../api'
import { Btn, Card, Badge, StatCard, Spinner, Empty, Alert, FG, Modal, ModalFooter, PageHeader, Section, toast } from '../../components/ui'

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

  const load = async () => {
    setLoading(true); setError(null)
    try { const d = await api('GET', '/actores'); setActores(toList(d, ['actores', 'data'])) }
    catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [])

  const ff = (k) => (e) => setForm(p => ({ ...p, [k]: e.target.value }))

  const crear = async () => {
    if (!form.nombre) { toast('Nombre requerido', 'error'); return }
    try {
      await api('POST', '/actores', {
        nombre: form.nombre, nacionalidad: form.nacionalidad,
        fechaNacimiento: form.fechaNacimiento, genero: form.genero || 'M',
        premios: (form.premios || '').split(',').map(x => x.trim()).filter(Boolean),
        esDirector: form.esDirector === true,
      })
      toast('Actor creado', 'success'); setModal(null); setForm({}); load()
    } catch (e) { toast(e.message, 'error') }
  }

  const agregarDir = async (id) => {
    try { await api('PATCH', `/actores/${id}/agregar-director`); toast('Label :Director agregado', 'success'); setModal(null); load() }
    catch (e) { toast(e.message, 'error') }
  }

  const vincular = async () => {
    if (!form.serieId) { toast('ID de serie requerido', 'error'); return }
    try {
      await api('POST', `/actores/${selected.id}/actua-en/${form.serieId}`, {
        personaje: form.personaje,
        temporadas: (form.temporadas || '').split(',').map(x => parseInt(x.trim())).filter(Boolean),
        rol: form.rol || 'secundario', fechaInicio: new Date().toISOString().split('T')[0],
      })
      toast('Actor vinculado a la serie', 'success'); setModal(null); setForm({})
    } catch (e) { toast(e.message, 'error') }
  }

  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <PageHeader
        title="Actores"
        subtitle="Gestión de actores y directores. Los nodos pueden tener múltiples labels."
        action={<Btn onClick={() => { setForm({}); setModal('crear') }}>+ Nuevo actor</Btn>}
      />
      {loading && <Spinner />}
      {error && <Alert type="error">{error}</Alert>}
      {!loading && !error && actores.length === 0 && <Empty message="Sin actores registrados" icon="◎" />}
      {!loading && !error && actores.length > 0 && (
        <Card style={{ overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead style={{ background: 'var(--off)' }}>
              <tr>{['Nombre','Labels','Nacionalidad','F. Nacimiento',''].map(h => (
                <th key={h} style={{ padding: '10px 16px', textAlign: 'left', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text-xs)', borderBottom: '1.5px solid var(--border)' }}>{h}</th>
              ))}</tr>
            </thead>
            <tbody>
              {actores.map(a => (
                <tr key={a.id} style={{ borderBottom: '1px solid var(--border)' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--off)'}
                  onMouseLeave={e => e.currentTarget.style.background = ''}>
                  <td style={{ padding: '12px 16px', fontWeight: 600 }}>{a.nombre || a.name || '-'}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', gap: 5 }}>
                      <Badge color="gray">Actor</Badge>
                      {(a.esDirector || a.es_director) && <Badge color="blue">Director</Badge>}
                    </div>
                  </td>
                  <td style={{ padding: '12px 16px', color: 'var(--text-xs)' }}>{a.nacionalidad || '-'}</td>
                  <td style={{ padding: '12px 16px', color: 'var(--text-xs)' }}>{a.fechaNacimiento || a.fecha_nacimiento || '-'}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', gap: 4 }}>
                      <Btn size="sm" variant="ghost" onClick={() => { setSelected(a); setModal('agregarDir') }}>+ Director</Btn>
                      <Btn size="sm" variant="ghost" onClick={() => { setSelected(a); setForm({}); setModal('vincular') }}>Vincular serie</Btn>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}

      {modal === 'crear' && (
        <Modal title="Nuevo actor" onClose={() => setModal(null)}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <FG label="Nombre *"><input value={form.nombre || ''} onChange={ff('nombre')} /></FG>
            <FG label="Nacionalidad"><input value={form.nacionalidad || ''} onChange={ff('nacionalidad')} /></FG>
            <FG label="F. nacimiento"><input type="date" value={form.fechaNacimiento || ''} onChange={ff('fechaNacimiento')} /></FG>
            <FG label="Género">
              <select value={form.genero || 'M'} onChange={ff('genero')}>
                <option value="M">Masculino</option><option value="F">Femenino</option><option value="NB">No binario</option>
              </select>
            </FG>
          </div>
          <FG label="Premios (separados por coma)"><input value={form.premios || ''} onChange={ff('premios')} placeholder="Oscar, Emmy…" /></FG>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', marginBottom: 0, textTransform: 'none', letterSpacing: 0, fontSize: 13.5 }}>
            <input type="checkbox" checked={form.esDirector || false} onChange={e => setForm(p => ({ ...p, esDirector: e.target.checked }))} style={{ width: 'auto' }} />
            También es Director
            <Badge color="blue">Multi-label</Badge>
          </label>
          <ModalFooter>
            <Btn variant="outline" onClick={() => setModal(null)}>Cancelar</Btn>
            <Btn onClick={crear}>Crear actor</Btn>
          </ModalFooter>
        </Modal>
      )}

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

      {modal === 'vincular' && selected && (
        <Modal title={`Vincular ${selected.nombre} a serie`} onClose={() => setModal(null)}>
          <FG label="ID de la serie *"><input value={form.serieId || ''} onChange={ff('serieId')} placeholder="ser_0001" /></FG>
          <FG label="Personaje"><input value={form.personaje || ''} onChange={ff('personaje')} /></FG>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <FG label="Temporadas (coma)"><input value={form.temporadas || ''} onChange={ff('temporadas')} placeholder="1,2,3" /></FG>
            <FG label="Rol">
              <select value={form.rol || 'secundario'} onChange={ff('rol')}>
                {['principal','secundario','recurrente','invitado'].map(r => <option key={r}>{r}</option>)}
              </select>
            </FG>
          </div>
          <ModalFooter>
            <Btn variant="outline" onClick={() => setModal(null)}>Cancelar</Btn>
            <Btn onClick={vincular}>Vincular</Btn>
          </ModalFooter>
        </Modal>
      )}
    </div>
  )
}

/* ═══════════════════════════════════════
   CSV
═══════════════════════════════════════ */
export function AdminCSV() {
  const [tipo, setTipo] = useState('series')
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const cargar = async () => {
    if (!file) { toast('Selecciona un archivo', 'error'); return }
    setLoading(true); setResult(null)
    const fd = new FormData(); fd.append('file', file); fd.append('tipo', tipo)
    try {
      const r = await fetch('http://localhost:8000/admin/cargar-csv', { method: 'POST', body: fd })
      if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.statusText)
      const data = await r.json()
      setResult({ ok: true, msg: data.message || 'CSV cargado exitosamente' })
    } catch (e) { setResult({ ok: false, msg: e.message }) }
    finally { setLoading(false) }
  }

  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <PageHeader title="Carga de datos CSV" subtitle="Importa nodos y relaciones a Neo4j desde archivos CSV." />
      <div style={{ maxWidth: 520 }}>
        <Card style={{ padding: '28px 32px' }}>
          <FG label="Tipo de entidad">
            <select value={tipo} onChange={e => setTipo(e.target.value)}>
              {['series','usuarios','actores','resenas','relaciones'].map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase()+t.slice(1)}</option>)}
            </select>
          </FG>
          <FG label="Archivo CSV">
            <input type="file" accept=".csv" onChange={e => setFile(e.target.files[0])}
              style={{ padding: '8px', cursor: 'pointer', fontSize: 13 }} />
          </FG>
          <Btn onClick={cargar} disabled={loading} style={{ marginTop: 4 }}>
            {loading ? 'Cargando…' : '↑ Subir y cargar'}
          </Btn>
          {result && (
            <div style={{ marginTop: 16 }}>
              <Alert type={result.ok ? 'success' : 'error'}>{result.ok ? '✓ ' : '✗ '}{result.msg}</Alert>
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}

/* ═══════════════════════════════════════
   ESTADÍSTICAS
═══════════════════════════════════════ */
export function AdminStats() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = async () => {
    setLoading(true); setError(null)
    try { setData(await api('GET', '/admin/estadisticas')) }
    catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [])

  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <PageHeader
        title="Estadísticas del grafo"
        subtitle="Estado actual de Neo4j y verificación de requisitos del proyecto."
        action={<Btn variant="outline" onClick={load}>↻ Actualizar</Btn>}
      />
      {loading && <Spinner />}
      {error && <Alert type="error">{error}</Alert>}
      {data && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 14 }}>
          {Object.entries(data).map(([k, v]) => {
            const isTotal = k === 'total_nodos' || k === 'totalNodos'
            const ok = isTotal && v >= 5000
            return (
              <StatCard key={k}
                label={k.replace(/_/g, ' ')}
                value={typeof v === 'number' ? v.toLocaleString() : String(v)}
                sub={isTotal ? (ok ? '✓ Cumple mínimo (5000+)' : '✗ Requiere 5000+ nodos') : undefined}
                accent={isTotal ? (ok ? 'var(--green)' : 'var(--red)') : undefined}
              />
            )
          })}
        </div>
      )}
    </div>
  )
}

/* ═══════════════════════════════════════
   CONSULTAS CYPHER
═══════════════════════════════════════ */
export function AdminConsultas() {
  const [result, setResult] = useState(null)
  const [activeQ, setActiveQ] = useState(null)
  const [loading, setLoading] = useState(false)

  const run = async (label, path, listKeys) => {
    setActiveQ(label); setLoading(true); setResult(null)
    try {
      const data = await api('GET', path)
      setResult({ label, list: toList(data, listKeys) })
    } catch (e) { toast(e.message, 'error') }
    finally { setLoading(false) }
  }

  const queries = [
    { label: 'Top series', desc: 'Por calificación y género', path: '/consultas/top-series', keys: ['series','data'] },
    { label: 'Usuarios influyentes', desc: 'Mayor impacto en la red', path: '/consultas/usuarios-influyentes', keys: ['usuarios','data'] },
    { label: 'Actores populares', desc: 'Por apariciones en series', path: '/consultas/actores-populares', keys: ['actores','data'] },
  ]

  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <PageHeader title="Consultas Cypher" subtitle="Análisis y estadísticas sobre el grafo de series." />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12, marginBottom: 28 }}>
        {queries.map(q => (
          <Card key={q.label} hover onClick={() => run(q.label, q.path, q.keys)}
            style={{ padding: '20px 22px', cursor: 'pointer', border: activeQ === q.label ? '1.5px solid var(--g400)' : undefined }}>
            <div style={{ fontFamily: 'Syne,sans-serif', fontWeight: 700, fontSize: 15, marginBottom: 5 }}>{q.label}</div>
            <div style={{ fontSize: 12.5, color: 'var(--text-xs)' }}>{q.desc}</div>
          </Card>
        ))}
      </div>
      {loading && <Spinner />}
      {result && (
        <Card style={{ overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1.5px solid var(--border)', fontFamily: 'Syne,sans-serif', fontWeight: 700, fontSize: 16 }}>{result.label}</div>
          {result.list.length === 0
            ? <div style={{ padding: 24 }}><Alert type="info">Sin resultados.</Alert></div>
            : <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead style={{ background: 'var(--off)' }}>
                  <tr>{Object.keys(result.list[0] || {}).slice(0, 5).map(k => (
                    <th key={k} style={{ padding: '10px 16px', textAlign: 'left', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text-xs)', borderBottom: '1.5px solid var(--border)' }}>{k}</th>
                  ))}</tr>
                </thead>
                <tbody>
                  {result.list.map((row, i) => (
                    <tr key={i} style={{ borderBottom: '1px solid var(--border)' }}>
                      {Object.values(row).slice(0, 5).map((v, j) => (
                        <td key={j} style={{ padding: '11px 16px', fontSize: 13.5, color: j === 0 ? 'var(--text)' : 'var(--text-sm)', fontWeight: j === 0 ? 600 : 400 }}>
                          {Array.isArray(v) ? v.join(', ') : String(v ?? '—')}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>}
        </Card>
      )}
    </div>
  )
}
