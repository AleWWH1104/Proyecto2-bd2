import { useState, useEffect } from 'react'
import { api, toList } from '../../api'
import { Btn, Card, Badge, RatingBar, StatCard, Spinner, Empty, Alert, FG, Modal, ModalFooter, PageHeader, toast, SerieCard } from '../../components/ui'

export default function AdminSeries() {
  const [series, setSeries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({ genero: '', plataforma: '', anio: '', calificacion: '' })
  const [modal, setModal] = useState(null) // null | 'crear' | 'editar' | 'ver' | 'similares'
  const [selected, setSelected] = useState(null)
  const [view, setView] = useState('grid') // 'grid' | 'table'
  const [form, setForm] = useState({})
  const [resenas, setResenas] = useState([])

  const load = async () => {
    setLoading(true); setError(null)
    try {
      const p = new URLSearchParams()
      Object.entries(filters).forEach(([k, v]) => { if (v) p.set(k, v) })
      const data = await api('GET', `/series?${p}`)
      setSeries(toList(data))
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const stats = {
    total: series.length,
    avg: series.length ? (series.reduce((s, x) => s + parseFloat(x.calificacion || 0), 0) / series.length).toFixed(1) : '—',
    activas: series.filter(x => x.activa === true || x.activa === 'True').length,
    emision: series.filter(x => x.estadoEmision === true || x.estadoEmision === 'True').length,
  }

  const openVer = async (s) => {
    setSelected(s); setModal('ver'); setResenas([])
    try { const r = await api('GET', `/series/${s.id}/resenas`); setResenas(toList(r, ['resenas', 'data'])) } catch {}
  }

  const openEditar = (s) => { setSelected(s); setForm({ ...s }); setModal('editar') }

  const crear = async () => {
    if (!form.titulo) { toast('Título requerido', 'error'); return }
    try {
      await api('POST', '/series', {
        titulo: form.titulo, sinopsis: form.sinopsis,
        anio: parseInt(form.anio) || 2024, calificacion: parseFloat(form.calificacion) || 7.5,
        numTemporadas: parseInt(form.numTemporadas) || 1, numEpisodios: parseInt(form.numEpisodios) || 10,
        estadoEmision: form.estadoEmision === 'true' || form.estadoEmision === true,
        activa: form.activa !== 'false' && form.activa !== false,
      })
      toast('Serie creada', 'success'); setModal(null); setForm({}); load()
    } catch (e) { toast(e.message, 'error') }
  }

  const editar = async () => {
    const body = {}
    if (form.titulo) body.titulo = form.titulo
    if (form.sinopsis) body.sinopsis = form.sinopsis
    if (form.anio) body.anio = parseInt(form.anio)
    if (form.calificacion) body.calificacion = parseFloat(form.calificacion)
    if (form.numTemporadas) body.numTemporadas = parseInt(form.numTemporadas)
    if (form.numEpisodios) body.numEpisodios = parseInt(form.numEpisodios)
    try {
      await api('PATCH', `/series/${selected.id}`, body)
      toast('Serie actualizada', 'success'); setModal(null); load()
    } catch (e) { toast(e.message, 'error') }
  }

  const eliminar = async (id) => {
    if (!confirm(`¿Eliminar ${id}?`)) return
    try { await api('DELETE', `/series/${id}`); toast('Eliminada', 'success'); load() }
    catch (e) { toast(e.message, 'error') }
  }

  const f = (k) => (e) => setFilters(prev => ({ ...prev, [k]: e.target.value }))
  const ff = (k) => (e) => setForm(prev => ({ ...prev, [k]: e.target.value }))

  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <PageHeader
        title="Catálogo de series"
        subtitle="Consulta, crea y gestiona todas las series en Neo4j."
        action={
          <div style={{ display: 'flex', gap: 8 }}>
            <Btn variant="outline" size="sm" onClick={() => setView(v => v === 'grid' ? 'table' : 'grid')}>
              {view === 'grid' ? '≡ Tabla' : '⊞ Tarjetas'}
            </Btn>
            <Btn onClick={() => { setForm({ anio: 2024, calificacion: 7.5, numTemporadas: 1, numEpisodios: 10, estadoEmision: false, activa: true }); setModal('crear') }}>
              + Nueva serie
            </Btn>
          </div>
        }
      />

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 12, marginBottom: 24 }}>
        <StatCard label="Total series" value={stats.total} />
        <StatCard label="Cal. promedio" value={stats.avg} sub="sobre 10" />
        <StatCard label="Activas" value={stats.activas} accent="var(--green)" />
        <StatCard label="En emisión" value={stats.emision} accent="var(--blue)" />
      </div>

      {/* Filters */}
      <Card style={{ padding: '16px 20px', marginBottom: 22, display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'flex-end' }}>
        {[['genero','Género','Drama…'],['plataforma','Plataforma','Netflix…']].map(([k, l, ph]) => (
          <div key={k} style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <label style={{ marginBottom: 0 }}>{l}</label>
            <input value={filters[k]} onChange={f(k)} placeholder={ph} style={{ width: 130 }} />
          </div>
        ))}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <label style={{ marginBottom: 0 }}>Año</label>
          <input type="number" value={filters.anio} onChange={f('anio')} placeholder="2022" style={{ width: 90 }} />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <label style={{ marginBottom: 0 }}>Cal. mín.</label>
          <input type="number" step="0.1" value={filters.calificacion} onChange={f('calificacion')} placeholder="7.0" style={{ width: 80 }} />
        </div>
        <Btn onClick={load}>Filtrar</Btn>
        <Btn variant="outline" onClick={() => { setFilters({ genero: '', plataforma: '', anio: '', calificacion: '' }); setTimeout(load, 50) }}>Limpiar</Btn>
      </Card>

      {/* Content */}
      {loading && <Spinner />}
      {error && <Alert type="error">{error}</Alert>}
      {!loading && !error && series.length === 0 && <Empty message="Sin series con esos filtros" />}

      {!loading && !error && series.length > 0 && view === 'grid' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px,1fr))', gap: 14 }}>
          {series.map(s => (
            <div key={s.id} style={{ position: 'relative' }}>
              <SerieCard serie={s} onClick={() => openVer(s)} />
              <div style={{ position: 'absolute', top: 10, right: 10, display: 'flex', gap: 5 }}>
                <button onClick={(e) => { e.stopPropagation(); openEditar(s) }}
                  style={{ background: 'rgba(255,255,255,.15)', border: 'none', borderRadius: 6, padding: '4px 8px', fontSize: 11, color: '#fff', cursor: 'pointer', backdropFilter: 'blur(4px)' }}>
                  Editar
                </button>
                <button onClick={(e) => { e.stopPropagation(); eliminar(s.id) }}
                  style={{ background: 'rgba(192,57,43,.7)', border: 'none', borderRadius: 6, padding: '4px 8px', fontSize: 11, color: '#fff', cursor: 'pointer' }}>
                  ✕
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && !error && series.length > 0 && view === 'table' && (
        <Card style={{ overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead style={{ background: 'var(--off)' }}>
              <tr>{['Título','Año','Calificación','Temp.','Estado','Activa',''].map(h => (
                <th key={h} style={{ padding: '10px 16px', textAlign: 'left', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text-xs)', borderBottom: '1.5px solid var(--border)' }}>{h}</th>
              ))}</tr>
            </thead>
            <tbody>
              {series.map(s => (
                <tr key={s.id} style={{ borderBottom: '1px solid var(--border)' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--off)'}
                  onMouseLeave={e => e.currentTarget.style.background = ''}>
                  <td style={{ padding: '12px 16px', fontWeight: 600, fontSize: 14 }}>{s.titulo}</td>
                  <td style={{ padding: '12px 16px', color: 'var(--text-xs)' }}>{s.anio}</td>
                  <td style={{ padding: '12px 16px' }}><RatingBar value={s.calificacion} /></td>
                  <td style={{ padding: '12px 16px', textAlign: 'center', color: 'var(--text-xs)' }}>{s.numTemporadas}</td>
                  <td style={{ padding: '12px 16px' }}><Badge color={s.estadoEmision === true || s.estadoEmision === 'True' ? 'blue' : 'gray'}>{s.estadoEmision === true || s.estadoEmision === 'True' ? 'En emisión' : 'Finalizada'}</Badge></td>
                  <td style={{ padding: '12px 16px' }}><Badge color={s.activa === true || s.activa === 'True' ? 'green' : 'gray'}>{s.activa === true || s.activa === 'True' ? 'Sí' : 'No'}</Badge></td>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', gap: 4 }}>
                      <Btn size="sm" variant="ghost" onClick={() => openVer(s)}>Ver</Btn>
                      <Btn size="sm" variant="ghost" onClick={() => openEditar(s)}>Editar</Btn>
                      <Btn size="sm" variant="danger" onClick={() => eliminar(s.id)}>✕</Btn>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}

      {/* Modal: Ver */}
      {modal === 'ver' && selected && (
        <Modal title={selected.titulo} onClose={() => setModal(null)} wide>
          <p style={{ fontSize: 13.5, color: 'var(--text-xs)', marginBottom: 18, lineHeight: 1.6 }}>{selected.sinopsis || 'Sin sinopsis.'}</p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 24px', marginBottom: 20 }}>
            {[['Año', selected.anio], ['Calificación', selected.calificacion], ['Temporadas', selected.numTemporadas], ['Episodios', selected.numEpisodios]].map(([k, v]) => (
              <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
                <span style={{ color: 'var(--text-xs)', fontSize: 13 }}>{k}</span>
                <span style={{ fontWeight: 600, fontSize: 13 }}>{v}</span>
              </div>
            ))}
          </div>
          {resenas.length > 0 && (
            <div>
              <h4 style={{ fontSize: 13, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text-xs)', marginBottom: 12 }}>Reseñas ({resenas.length})</h4>
              {resenas.map((r, i) => (
                <div key={i} style={{ borderLeft: '3px solid var(--g200)', paddingLeft: 14, marginBottom: 12 }}>
                  <div style={{ fontWeight: 600, fontSize: 13.5 }}>{r.titulo || 'Reseña'} <span style={{ color: 'var(--text-xs)', fontWeight: 400 }}>· {r.calificacion}/10</span></div>
                  <div style={{ fontSize: 12.5, color: 'var(--text-xs)', marginTop: 3 }}>{r.texto}</div>
                </div>
              ))}
            </div>
          )}
          <ModalFooter>
            <Btn variant="outline" onClick={() => setModal(null)}>Cerrar</Btn>
            <Btn variant="outline" onClick={() => { setModal(null); setTimeout(async () => { try { const d = await api('GET', `/series/${selected.id}/similares`); setSelected({ _similares: toList(d) }); setModal('similares') } catch (e) { toast(e.message, 'error') } }, 50) }}>Similares →</Btn>
          </ModalFooter>
        </Modal>
      )}

      {/* Modal: Similares */}
      {modal === 'similares' && selected?._similares && (
        <Modal title="Series similares" onClose={() => setModal(null)} wide>
          {selected._similares.length === 0
            ? <Empty message="Sin similares encontrados" />
            : <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(180px,1fr))', gap: 12 }}>
                {selected._similares.map(s => <SerieCard key={s.id} serie={s} />)}
              </div>}
          <ModalFooter><Btn variant="outline" onClick={() => setModal(null)}>Cerrar</Btn></ModalFooter>
        </Modal>
      )}

      {/* Modal: Crear / Editar */}
      {(modal === 'crear' || modal === 'editar') && (
        <Modal title={modal === 'crear' ? 'Nueva serie' : 'Editar serie'} onClose={() => setModal(null)}>
          <FG label="Título *"><input value={form.titulo || ''} onChange={ff('titulo')} /></FG>
          <FG label="Sinopsis"><textarea rows={3} value={form.sinopsis || ''} onChange={ff('sinopsis')} /></FG>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <FG label="Año"><input type="number" value={form.anio || ''} onChange={ff('anio')} /></FG>
            <FG label="Calificación"><input type="number" step="0.1" min="0" max="10" value={form.calificacion || ''} onChange={ff('calificacion')} /></FG>
            <FG label="Temporadas"><input type="number" value={form.numTemporadas || ''} onChange={ff('numTemporadas')} /></FG>
            <FG label="Episodios"><input type="number" value={form.numEpisodios || ''} onChange={ff('numEpisodios')} /></FG>
            <FG label="Estado">
              <select value={form.estadoEmision || 'false'} onChange={ff('estadoEmision')}>
                <option value="false">Finalizada</option>
                <option value="true">En emisión</option>
              </select>
            </FG>
            <FG label="Activa">
              <select value={form.activa === false || form.activa === 'false' ? 'false' : 'true'} onChange={ff('activa')}>
                <option value="true">Sí</option>
                <option value="false">No</option>
              </select>
            </FG>
          </div>
          <ModalFooter>
            <Btn variant="outline" onClick={() => setModal(null)}>Cancelar</Btn>
            <Btn onClick={modal === 'crear' ? crear : editar}>{modal === 'crear' ? 'Crear serie' : 'Guardar cambios'}</Btn>
          </ModalFooter>
        </Modal>
      )}
    </div>
  )
}