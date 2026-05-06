import { useState, useEffect } from 'react'
import { api, toList } from '../../api'
import { Btn, Card, Badge, RatingBar, Spinner, Empty, Alert, FG, Modal, ModalFooter, PageHeader, toast, SerieCard, StatCard } from '../../components/ui'

export default function AdminSeries() {
  const [series, setSeries] = useState([])
  const [aggs, setAggs] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({ genero: '', plataforma: '', anio: '', calificacion: '' })
  const [modal, setModal] = useState(null) // null | 'crear' | 'editar' | 'ver' | 'similares'
  const [selected, setSelected] = useState(null)
  const [view, setView] = useState('grid') // 'grid' | 'table'
  const [form, setForm] = useState({})
  const [resenas, setResenas] = useState([])
  const [selectedIds, setSelectedIds] = useState([])
  const [propForm, setPropForm] = useState({ json: '{"calificacion": 8.0}', nombres: '' })

  const load = async () => {
    setLoading(true); setError(null); setSelectedIds([])
    try {
      const p = new URLSearchParams()
      Object.entries(filters).forEach(([k, v]) => { if (v) p.set(k, v) })
      const data = await api('GET', `/series?${p}`)
      setSeries(toList(data))
      setAggs(data.agregaciones)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const openVer = async (s) => {
    setSelected(s); setModal('ver'); setResenas([])
    try {
      const [detalle, resenas] = await Promise.all([
        api('GET', `/series/${s.id}`),
        api('GET', `/series/${s.id}/resenas`),
      ])
      setSelected(detalle)
      setResenas(toList(resenas, ['resenas', 'data']))
    } catch {}
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
    const p = {}
    if (form.titulo) p.titulo = form.titulo
    if (form.sinopsis !== undefined) p.sinopsis = form.sinopsis
    if (form.anio) p.anio = parseInt(form.anio)
    if (form.calificacion !== undefined) p.calificacion = parseFloat(form.calificacion)
    if (form.numTemporadas) p.numTemporadas = parseInt(form.numTemporadas)
    if (form.numEpisodios) p.numEpisodios = parseInt(form.numEpisodios)
    
    // Convertir estados a booleanos para Neo4j
    p.estadoEmision = form.estadoEmision === 'true' || form.estadoEmision === true
    p.activa = form.activa === 'true' || form.activa === true || form.activa === 'True'

    try {
      // El backend espera { propiedades: { ... } }
      await api('PATCH', `/series/${selected.id}`, { propiedades: p })
      toast('Serie actualizada', 'success'); setModal(null); load()
    } catch (e) { toast(e.message, 'error') }
  }

  const eliminar = async (id) => {
    if (!confirm(`¿Eliminar ${id}?`)) return
    try { await api('DELETE', `/series/${id}`); toast('Eliminada', 'success'); load() }
    catch (e) { toast(e.message, 'error') }
  }

  const eliminarMasivo = async () => {
    if (!confirm(`¿Eliminar ${selectedIds.length} series?`)) return
    try {
      await api('DELETE', '/series/masivo', { ids: selectedIds })
      toast('Series eliminadas', 'success'); load()
    } catch (e) { toast(e.message, 'error') }
  }

  const toggleSelect = (id) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id])
  }

  const toggleAll = () => {
    if (selectedIds.length === series.length) setSelectedIds([])
    else setSelectedIds(series.map(s => s.id))
  }

  const masivoPropUpdate = async () => {
    let propiedades
    try { propiedades = JSON.parse(propForm.json) } catch { toast('JSON inválido — ej: {"calificacion":9.0}', 'error'); return }
    try {
      const r = await api('PATCH', '/series/masivo', { ids: selectedIds, propiedades })
      toast(`${r.actualizadas} series actualizadas`, 'success')
      setModal(null); setSelectedIds([]); load()
    } catch (e) { toast(e.message, 'error') }
  }

  const masivoPropDelete = async () => {
    const nombres = propForm.nombres.split(',').map(s => s.trim()).filter(Boolean)
    if (!nombres.length) { toast('Ingresa al menos 1 nombre', 'error'); return }
    try {
      const r = await api('DELETE', '/series/masivo/propiedades', { ids: selectedIds, nombres })
      toast(`Propiedades eliminadas en ${r.afectadas} series`, 'success')
      setModal(null); setSelectedIds([]); load()
    } catch (e) { toast(e.message, 'error') }
  }

  const singlePropDelete = async () => {
    const nombres = propForm.nombres.split(',').map(s => s.trim()).filter(Boolean)
    if (!nombres.length) { toast('Ingresa al menos 1 nombre', 'error'); return }
    try {
      await api('DELETE', `/series/${selected.id}/propiedades`, { nombres })
      toast('Propiedades eliminadas', 'success')
      setModal(null); load()
    } catch (e) { toast(e.message, 'error') }
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
      {aggs && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 28 }}>
          <StatCard label="Total Series" value={aggs.total} sub="En el catálogo" />
          <StatCard label="Calificación Promedio" value={aggs.promedio_calificacion?.toFixed(2) || '0.00'} sub="Global" accent="var(--green)" />
          <StatCard label="Géneros" value={aggs.por_genero?.length || 0} sub="Diferentes categorías" />
          <StatCard label="Plataformas" value={aggs.por_plataforma?.length || 0} sub="Donde se transmiten" />
        </div>
      )}

      {/* Bulk Actions Bar */}
      {selectedIds.length > 0 && (
        <Card style={{ padding: '12px 20px', marginBottom: 18, background: 'var(--g700)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ fontSize: 13.5, fontWeight: 600 }}>{selectedIds.length} items seleccionados</div>
          <div style={{ display: 'flex', gap: 8 }}>
            <Btn variant="outline" size="sm" style={{ color: '#fff', borderColor: 'rgba(255,255,255,.3)' }} onClick={() => setSelectedIds([])}>Cancelar</Btn>
            <Btn variant="outline" size="sm" style={{ color: '#fff', borderColor: 'rgba(255,255,255,.3)' }} onClick={() => { setPropForm({ json: '{"calificacion": 8.0}', nombres: '' }); setModal('masivoPropEdit') }}>Actualizar props</Btn>
            <Btn variant="outline" size="sm" style={{ color: '#fff', borderColor: 'rgba(255,255,255,.3)' }} onClick={() => { setPropForm({ json: '', nombres: '' }); setModal('masivoPropDel') }}>Quitar props</Btn>
            <Btn variant="danger" size="sm" style={{ background: '#e74c3c', color: '#fff' }} onClick={eliminarMasivo}>Eliminar selección</Btn>
          </div>
        </Card>
      )}

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
                <button onClick={(e) => { e.stopPropagation(); setSelected(s); setPropForm({ json: '', nombres: '' }); setModal('propDel') }}
                  style={{ background: 'rgba(52,73,94,.7)', border: 'none', borderRadius: 6, padding: '4px 8px', fontSize: 11, color: '#fff', cursor: 'pointer', backdropFilter: 'blur(4px)' }}>
                  –Props
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
              <tr>
                <th style={{ padding: '10px 16px', textAlign: 'left', width: 40, borderBottom: '1.5px solid var(--border)' }}>
                  <input type="checkbox" checked={selectedIds.length === series.length && series.length > 0} onChange={toggleAll} style={{ width: 16, height: 16, cursor: 'pointer' }} />
                </th>
                {['Título','Año','Calificación','Temp.','Eps.','Estado','Activa',''].map(h => (
                <th key={h} style={{ padding: '10px 16px', textAlign: 'left', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text-xs)', borderBottom: '1.5px solid var(--border)' }}>{h}</th>
              ))}</tr>
            </thead>
            <tbody>
              {series.map(s => (
                <tr key={s.id} style={{ borderBottom: '1px solid var(--border)', background: selectedIds.includes(s.id) ? 'var(--g50)' : '' }}
                  onMouseEnter={e => !selectedIds.includes(s.id) && (e.currentTarget.style.background = 'var(--off)')}
                  onMouseLeave={e => !selectedIds.includes(s.id) && (e.currentTarget.style.background = '')}>
                  <td style={{ padding: '12px 16px' }}>
                    <input type="checkbox" checked={selectedIds.includes(s.id)} onChange={() => toggleSelect(s.id)} style={{ width: 16, height: 16, cursor: 'pointer' }} />
                  </td>
                  <td style={{ padding: '12px 16px', fontWeight: 600, fontSize: 14 }}>{s.titulo}</td>
                  <td style={{ padding: '12px 16px', color: 'var(--text-xs)' }}>{s.anio}</td>
                  <td style={{ padding: '12px 16px' }}><RatingBar value={s.calificacion} /></td>
                  <td style={{ padding: '12px 16px', textAlign: 'center', color: 'var(--text-xs)' }}>{s.numTemporadas}</td>
                  <td style={{ padding: '12px 16px', textAlign: 'center', color: 'var(--text-xs)' }}>{s.numEpisodios}</td>
                  <td style={{ padding: '12px 16px' }}><Badge color={s.estadoEmision === true || s.estadoEmision === 'True' ? 'blue' : 'gray'}>{s.estadoEmision === true || s.estadoEmision === 'True' ? 'En emisión' : 'Finalizada'}</Badge></td>
                  <td style={{ padding: '12px 16px' }}><Badge color={s.activa === true || s.activa === 'True' ? 'green' : 'gray'}>{s.activa === true || s.activa === 'True' ? 'Sí' : 'No'}</Badge></td>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', gap: 4 }}>
                      <Btn size="sm" variant="ghost" onClick={() => openVer(s)}>Ver</Btn>
                      <Btn size="sm" variant="ghost" onClick={() => openEditar(s)}>Editar</Btn>
                      <Btn size="sm" variant="ghost" onClick={() => { setSelected(s); setPropForm({ json: '', nombres: '' }); setModal('propDel') }}>–Props</Btn>
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
                <span style={{ fontWeight: 600, fontSize: 13 }}>{v ?? '—'}</span>
              </div>
            ))}
          </div>

          {selected.generos?.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text-xs)', marginBottom: 8 }}>Géneros</div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {selected.generos.map(g => <Badge key={g.id || g}>{g.nombre || g}</Badge>)}
              </div>
            </div>
          )}

          {selected.plataformas?.length > 0 && (
            <div style={{ marginTop: 14 }}>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text-xs)', marginBottom: 8 }}>Plataformas</div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {selected.plataformas.map(p => <Badge key={p.id || p} color="blue">{p.nombre || p}</Badge>)}
              </div>
            </div>
          )}

          {selected.estudios?.length > 0 && (
            <div style={{ marginTop: 14 }}>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text-xs)', marginBottom: 8 }}>Estudios de producción</div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {selected.estudios.map(e => <Badge key={e.id} color="dark">{e.nombre}</Badge>)}
              </div>
            </div>
          )}

          {selected.actores?.length > 0 && (
            <div style={{ marginTop: 14 }}>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text-xs)', marginBottom: 8 }}>Elenco principal</div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                {selected.actores.map(a => (
                  <div key={a.id} style={{ fontSize: 13, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <span style={{ fontWeight: 600 }}>{a.nombre}</span>
                    <span style={{ color: 'var(--text-xs)' }}>as {a.personaje}</span>
                    {a.protagonista && <Badge color="green">TOP</Badge>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {selected.directores?.length > 0 && (
            <div style={{ marginTop: 14 }}>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text-xs)', marginBottom: 8 }}>Dirección</div>
              <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                {selected.directores.map(d => (
                  <div key={d.id} style={{ fontSize: 13 }}>
                    <span style={{ fontWeight: 600 }}>{d.nombre}</span>
                    {d.esPrincipal && <span style={{ color: 'var(--text-xs)', marginLeft: 4 }}>(Principal)</span>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {selected.similares?.length > 0 && (
            <div style={{ marginTop: 14 }}>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text-xs)', marginBottom: 8 }}>Series similares</div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {selected.similares.map(s => <Badge key={s.id} color="gray">{s.titulo}</Badge>)}
              </div>
            </div>
          )}

          {resenas.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <h4 style={{ fontSize: 13, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text-xs)', marginBottom: 12 }}>Reseñas ({resenas.length})</h4>
              {resenas.map((r, i) => (
                <div key={i} style={{ borderLeft: '3px solid var(--g200)', paddingLeft: 14, marginBottom: 12 }}>
                  <div style={{ fontWeight: 600, fontSize: 13.5 }}>{r.titulo || 'Reseña'} <span style={{ color: 'var(--text-xs)', fontWeight: 400 }}>· {r.puntuacion ?? r.calificacion}/10</span></div>
                  <div style={{ fontSize: 12.5, color: 'var(--text-xs)', marginTop: 3 }}>{r.texto}</div>
                </div>
              ))}
            </div>
          )}
          <ModalFooter>
            <Btn variant="outline" onClick={() => setModal(null)}>Cerrar</Btn>
          </ModalFooter>
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
      {/* Modal: Actualizar props masivo */}
      {modal === 'masivoPropEdit' && (
        <Modal title={`Actualizar propiedades — ${selectedIds.length} series`} onClose={() => setModal(null)}>
          <p style={{ fontSize: 13, color: 'var(--text-xs)', marginBottom: 14 }}>
            El JSON se fusionará (SET +=) sobre cada serie seleccionada. Las claves existentes se actualizan; las nuevas se agregan.
          </p>
          <FG label='Propiedades JSON (ej: {"calificacion": 9.0, "activa": true})'>
            <textarea rows={4} value={propForm.json} onChange={e => setPropForm(p => ({ ...p, json: e.target.value }))}
              style={{ fontFamily: 'monospace', fontSize: 12.5 }} />
          </FG>
          <ModalFooter>
            <Btn variant="outline" onClick={() => setModal(null)}>Cancelar</Btn>
            <Btn onClick={masivoPropUpdate}>Aplicar cambios</Btn>
          </ModalFooter>
        </Modal>
      )}

      {/* Modal: Eliminar props masivo */}
      {modal === 'masivoPropDel' && (
        <Modal title={`Eliminar propiedades — ${selectedIds.length} series`} onClose={() => setModal(null)}>
          <p style={{ fontSize: 13, color: 'var(--text-xs)', marginBottom: 14 }}>
            Ingresá los nombres de las propiedades separados por coma. Se eliminarán de todas las series seleccionadas.
          </p>
          <FG label="Nombres de propiedades (ej: calificacion, sinopsis)">
            <input value={propForm.nombres} onChange={e => setPropForm(p => ({ ...p, nombres: e.target.value }))}
              placeholder="prop1, prop2, prop3" />
          </FG>
          <ModalFooter>
            <Btn variant="outline" onClick={() => setModal(null)}>Cancelar</Btn>
            <Btn variant="danger" onClick={masivoPropDelete}>Eliminar propiedades</Btn>
          </ModalFooter>
        </Modal>
      )}

      {/* Modal: Eliminar props de una serie */}
      {modal === 'propDel' && selected && (
        <Modal title={`Eliminar propiedades — ${selected.titulo}`} onClose={() => setModal(null)}>
          <p style={{ fontSize: 13, color: 'var(--text-xs)', marginBottom: 14 }}>
            Ingresá los nombres de las propiedades a eliminar de esta serie, separados por coma.
          </p>
          <FG label="Nombres de propiedades (ej: sinopsis, activa)">
            <input value={propForm.nombres} onChange={e => setPropForm(p => ({ ...p, nombres: e.target.value }))}
              placeholder="prop1, prop2" />
          </FG>
          <ModalFooter>
            <Btn variant="outline" onClick={() => setModal(null)}>Cancelar</Btn>
            <Btn variant="danger" onClick={singlePropDelete}>Eliminar propiedades</Btn>
          </ModalFooter>
        </Modal>
      )}
    </div>
  )
}
