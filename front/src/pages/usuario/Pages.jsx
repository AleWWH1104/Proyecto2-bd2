import { useState, useEffect } from 'react'
import { api, toList } from '../../api'
import { Btn, Card, Badge, RatingBar, Spinner, Empty, Alert, FG, Modal, ModalFooter, PageHeader, SerieCard, toast } from '../../components/ui'

/* ═══════════════════════════════════════
   EXPLORAR
═══════════════════════════════════════ */
export function Explorar({ user }) {
  const [series, setSeries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({ genero: '', plataforma: '', anio: '', calificacion: '' })
  const [selected, setSelected] = useState(null)
  const [resenas, setResenas] = useState([])
  const [modalResena, setModalResena] = useState(false)
  const [formResena, setFormResena] = useState({})

  const load = async () => {
    setLoading(true); setError(null)
    try {
      const p = new URLSearchParams()
      Object.entries(filters).forEach(([k, v]) => { if (v) p.set(k, v) })
      setSeries(toList(await api('GET', `/series?${p}`)))
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [])

  const openSerie = async (s) => {
    setSelected(s); setResenas([])
    try { 
      const [detalle, res] = await Promise.all([
        api('GET', `/series/${s.id}`),
        api('GET', `/series/${s.id}/resenas`)
      ])
      setSelected(detalle)
      setResenas(toList(res)) 
    } catch {}
  }

  const like = async () => { 
    try { 
      await api('POST', `/usuarios/${user.id}/le-gusta/${selected.id}`, { 
        puntuacion: 5,
        notificarx: true 
      }); 
      toast('Guardado en likes ♥', 'success') 
    } catch (e) { toast(e.message, 'error') } 
  }
  const watchlist = async (prioridad = 3) => { 
    try { 
      await api('POST', `/usuarios/${user.id}/en-lista/${selected.id}`, { 
        prioridad,
        notificaciones: true
      }); 
      toast('Agregada a watchlist', 'success') 
    } catch (e) { toast(e.message, 'error') } 
  }
  const vista = async (porcentaje = 100, calificacion = 10) => { 
    try { 
      await api('POST', `/usuarios/${user.id}/vio/${selected.id}`, { 
        porcentajeVisto: porcentaje, 
        completada: porcentaje === 100,
        calificacion
      }); 
      toast('Marcada como vista ✓', 'success') 
    } catch (e) { toast(e.message, 'error') } 
  }

  const crearResena = async () => {
    if (!user) { toast('Inicia sesión primero', 'error'); return }
    try {
      await api('POST', `/series/${selected.id}/resenas`, { 
        titulo: formResena.titulo,
        texto: formResena.texto,
        puntuacion: parseInt(formResena.puntuacion) || 8, 
        contieneSpoilers: formResena.spoilers === 'true', 
        usuario_id: user.id,
        etiquetas: []
      })
      toast('Reseña publicada', 'success'); setModalResena(false); setFormResena({}); load();
    } catch (e) { toast(e.message, 'error') }
  }

  const f = (k) => (e) => setFilters(p => ({ ...p, [k]: e.target.value }))

  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <PageHeader title="Explorar series" subtitle="Descubre todo el catálogo." />

      <Card style={{ padding: '16px 20px', marginBottom: 22, display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'flex-end' }}>
        {[['genero','Género','Drama…'],['plataforma','Plataforma','Netflix…']].map(([k, l, ph]) => (
          <div key={k} style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <label style={{ marginBottom: 0 }}>{l}</label>
            <input value={filters[k]} onChange={f(k)} placeholder={ph} style={{ width: 130 }} />
          </div>
        ))}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <label style={{ marginBottom: 0 }}>Año</label>
          <input type="number" value={filters.anio} onChange={f('anio')} placeholder="2022" style={{ width: 88 }} />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <label style={{ marginBottom: 0 }}>Cal. mín.</label>
          <input type="number" step="0.1" value={filters.calificacion} onChange={f('calificacion')} placeholder="7.0" style={{ width: 78 }} />
        </div>
        <Btn onClick={load}>Buscar</Btn>
        <Btn variant="outline" onClick={() => { setFilters({ genero: '', plataforma: '', anio: '', calificacion: '' }); setTimeout(load, 50) }}>Limpiar</Btn>
      </Card>

      {loading && <Spinner />}
      {error && <Alert type="error">{error}</Alert>}
      {!loading && !error && series.length === 0 && <Empty message="Sin resultados" />}
      {!loading && !error && series.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(210px,1fr))', gap: 14 }}>
          {series.map(s => <SerieCard key={s.id} serie={s} onClick={() => openSerie(s)} />)}
        </div>
      )}

      {selected && !modalResena && (
        <Modal title={selected.titulo} onClose={() => setSelected(null)} wide>
          <p style={{ fontSize: 13.5, color: 'var(--text-xs)', lineHeight: 1.65, marginBottom: 18 }}>{selected.sinopsis || 'Sin sinopsis.'}</p>
          
          <div style={{ display: 'flex', gap: 16, marginBottom: 18, flexWrap: 'wrap' }}>
            <RatingBar value={selected.calificacion} />
            <span style={{ fontSize: 13, color: 'var(--text-xs)' }}>{selected.anio} · {selected.numTemporadas} temp. · {selected.numEpisodios} ep.</span>
          </div>

          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 20 }}>
            {selected.generos?.map(g => <Badge key={g.id || g}>{g.nombre || g}</Badge>)}
            {selected.plataformas?.map(p => <Badge key={p.id || p} color="blue">{p.nombre || p}</Badge>)}
          </div>

          {selected.actores?.length > 0 && (
            <div style={{ marginBottom: 20 }}>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text-xs)', marginBottom: 8 }}>Elenco</div>
              <div style={{ display: 'flex', gap: 10, overflowX: 'auto', paddingBottom: 8 }}>
                {selected.actores.slice(0, 5).map(a => (
                  <div key={a.id} style={{ fontSize: 12.5, whiteSpace: 'nowrap' }}>
                    <span style={{ fontWeight: 600 }}>{a.nombre}</span>
                    <span style={{ color: 'var(--text-xs)', marginLeft: 4 }}>as {a.personaje}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {user ? (
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 20, borderTop: '1px solid var(--border)', paddingTop: 20 }}>
              <Btn size="sm" onClick={like}>♥ Me gusta</Btn>
              <Btn size="sm" variant="outline" onClick={() => watchlist(3)}>+ Watchlist</Btn>
              <Btn size="sm" variant="outline" onClick={() => vista(100, 10)}>✓ Vista</Btn>
              <Btn size="sm" variant="ghost" onClick={() => setModalResena(true)}>+ Reseña</Btn>
            </div>
          ) : (
            <Alert type="info" style={{ marginBottom: 16 }}>Inicia sesión para interactuar con esta serie.</Alert>
          )}

          {resenas.length > 0 && (
            <div>
              <h4 style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text-xs)', marginBottom: 12 }}>Reseñas ({resenas.length})</h4>
              {resenas.map((r, i) => (
                <div key={i} style={{ borderLeft: '3px solid var(--g200)', paddingLeft: 14, marginBottom: 12 }}>
                  <div style={{ fontWeight: 600, fontSize: 13.5 }}>{r.titulo || 'Reseña'} <span style={{ color: 'var(--text-xs)', fontWeight: 400 }}>· {r.puntuacion}/10</span></div>
                  <div style={{ fontSize: 12.5, color: 'var(--text-xs)', marginTop: 3 }}>{r.texto}</div>
                </div>
              ))}
            </div>
          )}
          <ModalFooter><Btn variant="outline" onClick={() => setSelected(null)}>Cerrar</Btn></ModalFooter>
        </Modal>
      )}

      {modalResena && selected && (
        <Modal title="Escribir reseña" onClose={() => setModalResena(false)}>
          <FG label="Título"><input value={formResena.titulo || ''} onChange={e => setFormResena(p => ({ ...p, titulo: e.target.value }))} /></FG>
          <FG label="Texto"><textarea rows={4} value={formResena.texto || ''} onChange={e => setFormResena(p => ({ ...p, texto: e.target.value }))} /></FG>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <FG label="Calificación (0–10)"><input type="number" step="1" min="1" max="10" value={formResena.puntuacion || ''} onChange={e => setFormResena(p => ({ ...p, puntuacion: e.target.value }))} /></FG>
            <FG label="Contiene spoilers"><select value={formResena.spoilers || 'false'} onChange={e => setFormResena(p => ({ ...p, spoilers: e.target.value }))}><option value="false">No</option><option value="true">Sí</option></select></FG>
          </div>
          <ModalFooter>
            <Btn variant="outline" onClick={() => setModalResena(false)}>Cancelar</Btn>
            <Btn onClick={crearResena}>Publicar</Btn>
          </ModalFooter>
        </Modal>
      )}
    </div>
  )
}

/* ═══════════════════════════════════════
   RECOMENDACIONES
═══════════════════════════════════════ */
export function Recomendaciones({ user, onNavigate }) {
  const [tab, setTab] = useState('rec')
  const [series, setSeries] = useState([])
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({ genero: '', plataforma: '', anio: '' })
  const [selected, setSelected] = useState(null)

  const load = async (mode = tab) => {
    if (!user) return
    setLoading(true)
    try {
      let path = `/recomendaciones/${user.id}`
      if (mode === 'adv') path += '/avanzado'
      
      const p = mode === 'filt' ? new URLSearchParams(Object.fromEntries(Object.entries(filters).filter(([, v]) => v))) : new URLSearchParams()
      const data = await api('GET', `${path}?${p}`)
      setSeries(toList(data))
    } catch (e) { toast(e.message, 'error') }
    finally { setLoading(false) }
  }

  useEffect(() => { if (user) load() }, [user])

  if (!user) return (
    <div style={{ padding: '28px 32px' }}>
      <div style={{ maxWidth: 420, margin: '60px auto 0', textAlign: 'center' }}>
        <div style={{ fontSize: 48, marginBottom: 16, opacity: .3 }}>★</div>
        <h2 style={{ fontSize: 22, fontWeight: 800, marginBottom: 10 }}>Inicia sesión primero</h2>
        <p style={{ fontSize: 13.5, color: 'var(--text-xs)', lineHeight: 1.65, marginBottom: 24 }}>Las recomendaciones se generan con base en tus likes, historial y usuarios que sigues.</p>
        <Btn onClick={() => onNavigate('perfil')}>Ir a mi perfil →</Btn>
      </div>
    </div>
  )

  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <PageHeader title={`Para ti, ${user.nombre?.split(' ')[0] || user.id}`} subtitle="Basado en tus gustos y tu red." />

      <div style={{ display: 'flex', gap: 0, borderBottom: '1.5px solid var(--border)', marginBottom: 24 }}>
        {[['rec','Personalizadas'],['filt','Con filtros'],['adv','Híbrido (Avanzado)']].map(([id, label]) => (
          <button key={id} onClick={() => { setTab(id); load(id) }}
            style={{ padding: '10px 18px', fontSize: 13.5, fontWeight: 600, fontFamily: 'inherit', cursor: 'pointer', background: 'none', border: 'none', borderBottom: tab === id ? '2.5px solid var(--g500)' : '2px solid transparent', color: tab === id ? 'var(--text)' : 'var(--text-xs)', marginBottom: -1.5, transition: 'all .15s' }}>
            {label}
          </button>
        ))}
      </div>

      {tab === 'filt' && (
        <Card style={{ padding: '16px 20px', marginBottom: 22, display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'flex-end' }}>
          {[['genero','Género'],['plataforma','Plataforma'],['anio','Año']].map(([k, l]) => (
            <div key={k} style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              <label style={{ marginBottom: 0 }}>{l}</label>
              <input value={filters[k]} onChange={e => setFilters(p => ({ ...p, [k]: e.target.value }))} style={{ width: k === 'anio' ? 88 : 130 }} />
            </div>
          ))}
          <Btn onClick={() => load('filt')}>Buscar</Btn>
        </Card>
      )}

      {tab === 'adv' && (
        <Alert type="info" style={{ marginBottom: 22 }}>Este algoritmo utiliza <b>Jaccard Similarity</b> para encontrar usuarios con gustos casi idénticos a los tuyos y pondera la novedad y popularidad.</Alert>
      )}

      {loading && <Spinner />}
      {!loading && series.length === 0 && <Empty message="Sin recomendaciones disponibles" icon="★" />}
      {!loading && series.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(240px,1fr))', gap: 16 }}>
          {series.map(s => (
            <Card key={s.serie_id} style={{ padding: 16, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontWeight: 800, fontSize: 15, marginBottom: 4 }}>{s.titulo}</div>
                {s.usuarios_similares && <div style={{ fontSize: 11.5, color: 'var(--green-text)', marginBottom: 8 }}>Le gusta a {s.usuarios_similares} personas afines</div>}
                {s.score && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginBottom: 10 }}>
                    <Badge color="green">Score: {s.score}</Badge>
                    {s.bonus_social > 0 && <Badge color="blue">Red social +{s.bonus_social}</Badge>}
                    {s.bonus_genero > 0 && <Badge color="gray">Género +{s.bonus_genero}</Badge>}
                  </div>
                )}
                {s.muestra_usuarios?.length > 0 && (
                  <div style={{ fontSize: 11, color: 'var(--text-xs)', fontStyle: 'italic' }}>E.g. {s.muestra_usuarios.join(', ')}</div>
                )}
              </div>
              <Btn size="sm" variant="outline" style={{ marginTop: 14 }} onClick={() => setSelected(s)}>Ver más</Btn>
            </Card>
          ))}
        </div>
      )}

      {selected && (
        <Modal title={selected.titulo} onClose={() => setSelected(null)}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 16 }}>
            <div>
              <h4 style={{ fontSize: 11, textTransform: 'uppercase', color: 'var(--text-xs)', marginBottom: 8 }}>¿Por qué esta recomendación?</h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                {selected.score_jaccard !== undefined && <StatCard label="Similitud (Jaccard)" value={selected.score_jaccard} />}
                {selected.novedad !== undefined && <StatCard label="Factor Novedad" value={selected.novedad} />}
                {selected.popularidad !== undefined && <StatCard label="Popularidad Global" value={selected.popularidad} />}
                {selected.coincidencias !== undefined && <StatCard label="Coincidencias" value={selected.coincidencias} />}
              </div>
            </div>
            <Btn onClick={() => { onNavigate('explorar'); setSelected(null) }}>Ir a Explorar para ver detalles</Btn>
          </div>
          <ModalFooter><Btn variant="outline" onClick={() => setSelected(null)}>Cerrar</Btn></ModalFooter>
        </Modal>
      )}
    </div>
  )
}

function StatCard({ label, value }) {
  return (
    <div style={{ background: 'var(--off)', padding: '10px 12px', borderRadius: 8, border: '1px solid var(--border)' }}>
      <div style={{ fontSize: 10, color: 'var(--text-xs)', textTransform: 'uppercase', marginBottom: 2 }}>{label}</div>
      <div style={{ fontSize: 15, fontWeight: 700 }}>{value}</div>
    </div>
  )
}

/* ═══════════════════════════════════════
   PERFIL
═══════════════════════════════════════ */
export function Perfil({ user, onLogin, onRegister, onLogout, onUpdate }) {
  const [loginId, setLoginId] = useState('')
  const [regForm, setRegForm] = useState({})
  const [modal, setModal] = useState(null)
  const [editForm, setEditForm] = useState({})
  const [followId, setFollowId] = useState('')
  const [fullProfile, setFullProfile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [modalResena, setModalResena] = useState(false)
  const [formResena, setFormResena] = useState({})
  const [selected, setSelected] = useState(null)
  const [vioModal, setVioModal] = useState(null)
  const [vioForm, setVioForm] = useState({})
  const [bulkVioOpen, setBulkVioOpen] = useState(false)
  const [bulkVioItems, setBulkVioItems] = useState([])
  const [likeSelecting, setLikeSelecting] = useState(false)
  const [likeSelection, setLikeSelection] = useState([])

  const loadProfile = async () => {
    if (!user?.id) return
    setLoading(true)
    try {
      const data = await api('GET', `/usuarios/${user.id}/perfil`)
      setFullProfile(data)
    } catch (e) { toast(e.message, 'error') }
    finally { setLoading(false) }
  }

  useEffect(() => { loadProfile() }, [user?.id])

  const doLogin = async () => {
    if (!loginId) { toast('Ingresa un ID', 'error'); return }
    try { const u = await api('GET', `/usuarios/${loginId}`); onLogin(u); toast(`Bienvenido, ${u.nombre || u.id}!`, 'success') }
    catch { toast('Usuario no encontrado', 'error') }
  }

  const doRegister = async () => {
    if (!regForm.nombre || !regForm.email) { toast('Nombre y email requeridos', 'error'); return }
    try {
      const u = await api('POST', '/usuarios', {
        nombre: regForm.nombre,
        email: regForm.email,
        edad: parseInt(regForm.edad) || 18,
        activo: true
      })
      onRegister(u); toast('¡Cuenta creada!', 'success'); setModal(null)
    } catch (e) { toast(e.message, 'error') }
  }

  const doUpdate = async () => {
    const p = {}
    if (editForm.nombre) p.nombre = editForm.nombre
    if (editForm.edad) p.edad = parseInt(editForm.edad)
    try { 
      const updated = await api('PATCH', `/usuarios/${user.id}`, { propiedades: p }); 
      onUpdate(updated); 
      toast('Perfil actualizado', 'success'); 
      setModal(null) 
    }
    catch (e) { toast(e.message, 'error') }
  }

  const doFollow = async () => {
    if (!followId) { toast('Ingresa un ID', 'error'); return }
    try { 
      await api('POST', `/usuarios/${user.id}/sigue/${followId}`, { 
        notificaciones: true
      }); 
      toast(`Ahora sigues a ${followId}`, 'success'); 
      setFollowId('');
      loadProfile()
    }
    catch (e) { toast(e.message, 'error') }
  }

  const doUnfollow = async (targetId) => {
    try {
      await api('DELETE', `/usuarios/${user.id}/sigue/${targetId}`)
      toast('Dejaste de seguir al usuario', 'success')
      loadProfile()
    } catch (e) { toast(e.message, 'error') }
  }

  const deleteResena = async (id) => {
    if (!confirm('¿Eliminar esta reseña?')) return
    try {
      await api('DELETE', `/resenas/${id}`)
      toast('Reseña eliminada', 'success')
      loadProfile()
    } catch (e) { toast(e.message, 'error') }
  }

  const openEditResena = (r) => {
    setFormResena({ ...r, spoilers: r.contieneSpoilers ? 'true' : 'false' })
    setSelected({ id: r.serie_id, titulo: r.serie_titulo || r.serie_id })
    setModalResena(true)
  }

  const crearResena = async () => {
    if (!user) { toast('Inicia sesión primero', 'error'); return }
    try {
      if (formResena.id) {
        // Editar
        await api('PATCH', `/resenas/${formResena.id}`, { 
          propiedades: {
            texto: formResena.texto,
            puntuacion: parseInt(formResena.puntuacion),
            titulo: formResena.titulo
          } 
        })
        toast('Reseña actualizada', 'success')
      } else {
        // Crear
        await api('POST', '/resenas', { 
          titulo: formResena.titulo,
          texto: formResena.texto,
          puntuacion: parseInt(formResena.puntuacion) || 8, 
          contieneSpoilers: formResena.spoilers === 'true', 
          usuario_id: user.id,
          serie_id: selected.id,
          etiquetas: []
        })
        toast('Reseña publicada', 'success')
      }
      setModalResena(false); setFormResena({}); loadProfile()
    } catch (e) { toast(e.message, 'error') }
  }

  const removeLike = async (serieId) => {
    try {
      await api('DELETE', `/usuarios/${user.id}/le-gusta/${serieId}`)
      toast('Like eliminado', 'success')
      loadProfile()
    } catch (e) { toast(e.message, 'error') }
  }

  const removeWatchlist = async (serieId) => {
    try {
      await api('DELETE', `/usuarios/${user.id}/en-lista/${serieId}`)
      toast('Quitada de watchlist', 'success')
      loadProfile()
    } catch (e) { toast(e.message, 'error') }
  }

  const removeVio = async (serieId) => {
    try {
      await api('DELETE', `/usuarios/${user.id}/vio/${serieId}`)
      toast('Eliminada del historial', 'success')
      loadProfile()
    } catch (e) { toast(e.message, 'error') }
  }

  const toggleLikeSelect = (id) => setLikeSelection(prev =>
    prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
  )

  const removeLikeMasivo = async () => {
    if (likeSelection.length === 0) return
    try {
      await api('DELETE', `/usuarios/${user.id}/le-gusta/masivo`, { serie_ids: likeSelection })
      toast(`${likeSelection.length} like(s) eliminado(s)`, 'success')
      setLikeSelection([]); setLikeSelecting(false); loadProfile()
    } catch (e) { toast(e.message, 'error') }
  }

  const openBulkVio = () => {
    setBulkVioItems((fullProfile.series_vistas || []).map(s => ({
      serie_id: s.serie_id,
      titulo: s.titulo,
      porcentajeVisto: s.porcentajeVisto ?? 0,
      completada: s.completada ?? false,
      calificacion: s.calificacion ?? '',
    })))
    setBulkVioOpen(true)
  }

  const updateBulkItem = (serie_id, field, value) => {
    setBulkVioItems(prev => prev.map(item =>
      item.serie_id === serie_id ? { ...item, [field]: value } : item
    ))
  }

  const saveBulkVio = async () => {
    const items = bulkVioItems.map(item => ({
      serie_id: item.serie_id,
      porcentajeVisto: parseFloat(item.porcentajeVisto) || 0,
      completada: item.completada === true || item.completada === 'true',
      ...(item.calificacion !== '' && { calificacion: parseFloat(item.calificacion) }),
    }))
    try {
      const res = await api('PATCH', `/usuarios/${user.id}/vio/masivo`, { items })
      toast(`${res.afectados} relaciones actualizadas`, 'success')
      setBulkVioOpen(false); loadProfile()
    } catch (e) { toast(e.message, 'error') }
  }

  const openEditVio = (s) => {
    setVioModal(s)
    setVioForm({ porcentajeVisto: s.porcentajeVisto ?? '', completada: s.completada ?? false, calificacion: s.calificacion ?? '' })
  }

  const saveVio = async () => {
    const body = {}
    if (vioForm.porcentajeVisto !== '') body.porcentajeVisto = parseFloat(vioForm.porcentajeVisto)
    if (vioForm.calificacion !== '') body.calificacion = parseFloat(vioForm.calificacion)
    body.completada = vioForm.completada === true || vioForm.completada === 'true'
    try {
      await api('PATCH', `/usuarios/${user.id}/vio/${vioModal.serie_id}`, body)
      toast('Progreso actualizado', 'success')
      setVioModal(null); loadProfile()
    } catch (e) { toast(e.message, 'error') }
  }

  if (!user) return (
    <div style={{ padding: '28px 32px 48px' }}>
      <PageHeader title="Mi perfil" subtitle="Inicia sesión o crea una cuenta." />
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, maxWidth: 600 }}>
        <Card style={{ padding: '28px 28px' }}>
          <h3 style={{ fontSize: 17, marginBottom: 18 }}>Iniciar sesión</h3>
          <FG label="ID de usuario"><input value={loginId} onChange={e => setLoginId(e.target.value)} placeholder="usr_xxxxxxxx" onKeyDown={e => e.key === 'Enter' && doLogin()} /></FG>
          <Btn style={{ width: '100%', justifyContent: 'center' }} onClick={doLogin}>Entrar</Btn>
        </Card>
        <Card style={{ padding: '28px 28px' }}>
          <h3 style={{ fontSize: 17, marginBottom: 12 }}>Crear cuenta</h3>
          <p style={{ fontSize: 13, color: 'var(--text-xs)', lineHeight: 1.6, marginBottom: 18 }}>Regístrate para acceder a recomendaciones personalizadas y seguir a otros.</p>
          <Btn variant="outline" style={{ width: '100%', justifyContent: 'center' }} onClick={() => setModal('registro')}>Registrarse →</Btn>
        </Card>
      </div>

      {modal === 'registro' && (
        <Modal title="Crear cuenta" onClose={() => setModal(null)}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <FG label="Nombre *"><input value={regForm.nombre || ''} onChange={e => setRegForm(p => ({ ...p, nombre: e.target.value }))} /></FG>
            <FG label="Email *"><input type="email" value={regForm.email || ''} onChange={e => setRegForm(p => ({ ...p, email: e.target.value }))} /></FG>
            <FG label="Edad"><input type="number" value={regForm.edad || ''} onChange={e => setRegForm(p => ({ ...p, edad: e.target.value }))} /></FG>
          </div>
          <ModalFooter>
            <Btn variant="outline" onClick={() => setModal(null)}>Cancelar</Btn>
            <Btn onClick={doRegister}>Crear cuenta</Btn>
          </ModalFooter>
        </Modal>
      )}
    </div>
  )

  const initials = (user.nombre || 'U').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
  const hue = (user.id?.charCodeAt(4) || 50) * 7 % 360

  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <PageHeader title="Mi perfil"
        action={
          <div style={{ display: 'flex', gap: 8 }}>
            <Btn variant="outline" onClick={() => { setEditForm({ nombre: user.nombre, edad: user.edad }); setModal('editar') }}>Editar perfil</Btn>
            <Btn variant="ghost" onClick={onLogout}>Cerrar sesión</Btn>
          </div>
        }
      />
      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: 24 }}>
        {/* Profile card */}
        <div>
          <Card style={{ padding: '28px 24px', marginBottom: 16 }}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', marginBottom: 22 }}>
              <div style={{ width: 72, height: 72, borderRadius: '50%', background: `hsl(${hue},25%,35%)`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, fontFamily: 'Syne,sans-serif', fontWeight: 800, color: '#fff', marginBottom: 14 }}>
                {initials}
              </div>
              <div style={{ fontFamily: 'Syne,sans-serif', fontWeight: 700, fontSize: 18 }}>{user.nombre || user.id}</div>
              <div style={{ fontSize: 12.5, color: 'var(--text-xs)', marginTop: 3 }}>{user.email || ''}</div>
              <div style={{ marginTop: 10 }}><Badge color={user.activo ? 'green' : 'gray'}>{user.activo ? 'Activo' : 'Inactivo'}</Badge></div>
            </div>
            <div style={{ borderTop: '1.5px solid var(--border)', paddingTop: 18 }}>
              {[['ID', user.id], ['Edad', user.edad || '-'], ['Desde', user.fechaRegistro || '-']].map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--border)', fontSize: 13 }}>
                  <span style={{ color: 'var(--text-xs)' }}>{k}</span>
                  <span style={{ fontWeight: 500 }}>{v}</span>
                </div>
              ))}
            </div>
          </Card>

          <Card style={{ padding: '20px 24px' }}>
            <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 14 }}>Seguir a usuario</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <input value={followId} onChange={e => setFollowId(e.target.value)} placeholder="usr_xxxxxxxx" style={{ width: '100%' }} onKeyDown={e => e.key === 'Enter' && doFollow()} />
              <Btn variant="outline" onClick={doFollow} style={{ justifyContent: 'center' }}>Seguir</Btn>
            </div>
          </Card>
        </div>

        {/* Right column: Lists */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {loading && <Spinner />}
          
          {fullProfile && (
            <>
              <Section title={`Watchlist (${fullProfile.series_en_lista?.length || 0})`}>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {fullProfile.series_en_lista?.length > 0 ? fullProfile.series_en_lista.map(s => (
                    <div key={s.serie_id} style={{ display: 'flex', alignItems: 'center', background: 'var(--blue-bg)', borderRadius: 6, paddingRight: 4 }}>
                      <Badge color="blue" style={{ marginRight: 0 }}>{s.titulo} <span style={{ opacity: .6, marginLeft: 4 }}>P{s.prioridad}</span></Badge>
                      <button onClick={() => removeWatchlist(s.serie_id)} style={{ background: 'none', border: 'none', color: 'var(--blue-text)', cursor: 'pointer', fontSize: 16, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 4px', opacity: .7 }}>×</button>
                    </div>
                  )) : <div style={{ fontSize: 13, color: 'var(--text-xs)' }}>Tu lista está vacía.</div>}
                </div>
              </Section>

              <Section
                title={`Series que te gustan (${fullProfile.series_que_le_gustan?.length || 0})`}
                action={fullProfile.series_que_le_gustan?.length > 1 && (
                  likeSelecting ? (
                    <div style={{ display: 'flex', gap: 6 }}>
                      <Btn size="sm" variant="outline" onClick={() => { setLikeSelecting(false); setLikeSelection([]) }}>Cancelar</Btn>
                      <Btn size="sm" variant="danger" style={{ background: '#e74c3c', color: '#fff' }} onClick={removeLikeMasivo} disabled={likeSelection.length === 0}>
                        Eliminar {likeSelection.length > 0 ? `(${likeSelection.length})` : ''}
                      </Btn>
                    </div>
                  ) : (
                    <Btn size="sm" variant="outline" onClick={() => setLikeSelecting(true)}>Seleccionar</Btn>
                  )
                )}
              >
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {fullProfile.series_que_le_gustan?.length > 0 ? fullProfile.series_que_le_gustan.map(s => {
                    const sel = likeSelecting && likeSelection.includes(s.serie_id)
                    return (
                      <div key={s.serie_id} onClick={() => likeSelecting && toggleLikeSelect(s.serie_id)}
                        style={{ display: 'flex', alignItems: 'center', background: sel ? '#c0392b22' : 'var(--green-bg)', borderRadius: 6, paddingRight: 4, cursor: likeSelecting ? 'pointer' : 'default', outline: sel ? '2px solid #e74c3c' : 'none' }}>
                        {likeSelecting && (
                          <input type="checkbox" checked={sel} onChange={() => toggleLikeSelect(s.serie_id)}
                            onClick={e => e.stopPropagation()} style={{ margin: '0 6px', cursor: 'pointer' }} />
                        )}
                        <Badge color="green" style={{ marginRight: 0 }}>{s.titulo} <span style={{ opacity: .8, marginLeft: 4 }}>★{s.puntuacion}</span></Badge>
                        {!likeSelecting && (
                          <button onClick={() => removeLike(s.serie_id)} style={{ background: 'none', border: 'none', color: 'var(--green-text)', cursor: 'pointer', fontSize: 16, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 4px', opacity: .7 }}>×</button>
                        )}
                      </div>
                    )
                  }) : <div style={{ fontSize: 13, color: 'var(--text-xs)' }}>Aún no has dado likes.</div>}
                </div>
              </Section>

              <Section title={`Historial de vistas (${fullProfile.series_vistas?.length || 0})`} action={fullProfile.series_vistas?.length > 1 && <Btn size="sm" variant="outline" onClick={openBulkVio}>Editar múltiple</Btn>}>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {fullProfile.series_vistas?.length > 0 ? fullProfile.series_vistas.map(s => (
                    <div key={s.serie_id} style={{ display: 'flex', alignItems: 'center', background: 'var(--gray-bg)', borderRadius: 6, paddingRight: 4 }}>
                      <Badge color="gray" style={{ marginRight: 0 }}>{s.titulo} <span style={{ opacity: .6, marginLeft: 4 }}>{s.porcentajeVisto}%</span></Badge>
                      <button onClick={() => openEditVio(s)} style={{ background: 'none', border: 'none', color: 'var(--gray-text)', cursor: 'pointer', fontSize: 13, padding: '0 5px', opacity: .8 }} title="Editar progreso">✎</button>
                      <button onClick={() => removeVio(s.serie_id)} style={{ background: 'none', border: 'none', color: 'var(--gray-text)', cursor: 'pointer', fontSize: 16, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 4px', opacity: .7 }}>×</button>
                    </div>
                  )) : <div style={{ fontSize: 13, color: 'var(--text-xs)' }}>No has marcado series como vistas.</div>}
                </div>
              </Section>

              <Section title={`Siguiendo (${fullProfile.usuarios_que_sigue?.length || 0})`}>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {fullProfile.usuarios_que_sigue?.length > 0 ? fullProfile.usuarios_que_sigue.map(u => (
                    <div key={u.usuario_id} style={{ display: 'flex', alignItems: 'center', background: 'var(--dark-bg)', borderRadius: 6, paddingRight: 4 }}>
                      <Badge color="dark" style={{ marginRight: 0 }}>{u.nombre} {u.mutuo && '↔'}</Badge>
                      <button onClick={() => doUnfollow(u.usuario_id)} style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', fontSize: 16, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 4px', opacity: .7 }}>×</button>
                    </div>
                  )) : <div style={{ fontSize: 13, color: 'var(--text-xs)' }}>No sigues a nadie todavía.</div>}
                </div>
              </Section>

              <Section title={`Mis Reseñas (${fullProfile.resenas?.length || 0})`}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {fullProfile.resenas?.length > 0 ? fullProfile.resenas.map(r => (
                    <Card key={r.id} style={{ padding: '12px 16px', borderLeft: '4px solid var(--g500)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                          <div style={{ fontWeight: 700, fontSize: 14 }}>{r.titulo || 'Sin título'} <span style={{ fontWeight: 400, color: 'var(--text-xs)', marginLeft: 8 }}>Sobre: {r.serie_titulo || r.serie_id}</span></div>
                          <div style={{ fontSize: 13, marginTop: 4 }}>{r.texto}</div>
                          <div style={{ marginTop: 6, display: 'flex', gap: 8, alignItems: 'center' }}>
                            <Badge color="green">★ {r.puntuacion}/10</Badge>
                            <span style={{ fontSize: 11, color: 'var(--text-xs)' }}>{r.fecha}</span>
                          </div>
                        </div>
                        <div style={{ display: 'flex', gap: 6 }}>
                          <Btn size="sm" variant="outline" onClick={() => openEditResena(r)}>Editar</Btn>
                          <Btn size="sm" variant="danger" onClick={() => deleteResena(r.id)}>✕</Btn>
                        </div>
                      </div>
                    </Card>
                  )) : <div style={{ fontSize: 13, color: 'var(--text-xs)' }}>No has escrito ninguna reseña.</div>}
                </div>
              </Section>
            </>
          )}
        </div>
      </div>

      {modal === 'editar' && (
        <Modal title="Editar perfil" onClose={() => setModal(null)}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <FG label="Nombre"><input value={editForm.nombre || ''} onChange={e => setEditForm(p => ({ ...p, nombre: e.target.value }))} /></FG>
            <FG label="Edad"><input type="number" value={editForm.edad || ''} onChange={e => setEditForm(p => ({ ...p, edad: e.target.value }))} /></FG>
          </div>
          <ModalFooter>
            <Btn variant="outline" onClick={() => setModal(null)}>Cancelar</Btn>
            <Btn onClick={doUpdate}>Guardar</Btn>
          </ModalFooter>
        </Modal>
      )}

      {bulkVioOpen && (
        <Modal title="Editar progreso de múltiples series" onClose={() => setBulkVioOpen(false)} wide>
          <p style={{ fontSize: 13, color: 'var(--text-xs)', marginBottom: 16 }}>
            Edita las propiedades de la relación <strong>VIO</strong> para varias series a la vez. Se actualizarán todas al guardar.
          </p>
          <div style={{ maxHeight: 420, overflowY: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
              <thead style={{ background: 'var(--off)', position: 'sticky', top: 0 }}>
                <tr>
                  {['Serie', '% Visto', 'Completada', 'Calificación'].map(h => (
                    <th key={h} style={{ padding: '8px 12px', textAlign: 'left', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.07em', color: 'var(--text-xs)', borderBottom: '1.5px solid var(--border)' }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {bulkVioItems.map(item => (
                  <tr key={item.serie_id} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '10px 12px', fontWeight: 600, maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{item.titulo}</td>
                    <td style={{ padding: '8px 12px' }}>
                      <input type="number" min="0" max="100" step="1" value={item.porcentajeVisto}
                        onChange={e => updateBulkItem(item.serie_id, 'porcentajeVisto', e.target.value)}
                        style={{ width: 70 }} />
                    </td>
                    <td style={{ padding: '8px 12px' }}>
                      <select value={item.completada === true || item.completada === 'true' ? 'true' : 'false'}
                        onChange={e => updateBulkItem(item.serie_id, 'completada', e.target.value)}
                        style={{ width: 70 }}>
                        <option value="true">Sí</option>
                        <option value="false">No</option>
                      </select>
                    </td>
                    <td style={{ padding: '8px 12px' }}>
                      <input type="number" min="0" max="10" step="0.5" value={item.calificacion}
                        onChange={e => updateBulkItem(item.serie_id, 'calificacion', e.target.value)}
                        placeholder="—" style={{ width: 70 }} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <ModalFooter>
            <Btn variant="outline" onClick={() => setBulkVioOpen(false)}>Cancelar</Btn>
            <Btn onClick={saveBulkVio}>Guardar {bulkVioItems.length} relaciones</Btn>
          </ModalFooter>
        </Modal>
      )}

      {vioModal && (
        <Modal title={`Editar progreso — ${vioModal.titulo}`} onClose={() => setVioModal(null)}>
          <p style={{ fontSize: 13, color: 'var(--text-xs)', marginBottom: 18 }}>
            Actualiza las propiedades de la relación <strong>VIO</strong> entre tu usuario y esta serie.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <FG label="% Visto (0–100)">
              <input type="number" min="0" max="100" step="1" value={vioForm.porcentajeVisto} onChange={e => setVioForm(p => ({ ...p, porcentajeVisto: e.target.value }))} />
            </FG>
            <FG label="Calificación (0–10)">
              <input type="number" min="0" max="10" step="0.5" value={vioForm.calificacion} onChange={e => setVioForm(p => ({ ...p, calificacion: e.target.value }))} />
            </FG>
            <FG label="Completada">
              <select value={vioForm.completada === true || vioForm.completada === 'true' ? 'true' : 'false'} onChange={e => setVioForm(p => ({ ...p, completada: e.target.value }))}>
                <option value="true">Sí</option>
                <option value="false">No</option>
              </select>
            </FG>
          </div>
          <ModalFooter>
            <Btn variant="outline" onClick={() => setVioModal(null)}>Cancelar</Btn>
            <Btn onClick={saveVio}>Guardar cambios</Btn>
          </ModalFooter>
        </Modal>
      )}

      {modalResena && (
        <Modal title={formResena.id ? "Editar reseña" : "Escribir reseña"} onClose={() => setModalResena(false)}>
          <FG label="Título"><input value={formResena.titulo || ''} onChange={e => setFormResena(p => ({ ...p, titulo: e.target.value }))} /></FG>
          <FG label="Texto"><textarea rows={4} value={formResena.texto || ''} onChange={e => setFormResena(p => ({ ...p, texto: e.target.value }))} /></FG>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <FG label="Calificación (0–10)"><input type="number" step="0.5" min="0" max="10" value={formResena.puntuacion || ''} onChange={e => setFormResena(p => ({ ...p, puntuacion: e.target.value }))} /></FG>
            {!formResena.id && (
              <FG label="Contiene spoilers"><select value={formResena.spoilers || 'false'} onChange={e => setFormResena(p => ({ ...p, spoilers: e.target.value }))}><option value="false">No</option><option value="true">Sí</option></select></FG>
            )}
          </div>
          <ModalFooter>
            <Btn variant="outline" onClick={() => setModalResena(false)}>Cancelar</Btn>
            <Btn onClick={crearResena}>{formResena.id ? 'Guardar cambios' : 'Publicar'}</Btn>
          </ModalFooter>
        </Modal>
      )}
    </div>
  )
}

/* ═══════════════════════════════════════
   BUSCAR USUARIOS
═══════════════════════════════════════ */
export function BuscarUsuarios({ user, onLogin }) {
  const [filters, setFilters] = useState({ edad_min: '', edad_max: '', activo: '' })
  const [usuarios, setUsuarios] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = async () => {
    setLoading(true); setError(null)
    try { 
      const p = new URLSearchParams()
      if (filters.edad_min) p.set('edad_min', filters.edad_min)
      if (filters.edad_max) p.set('edad_max', filters.edad_max)
      if (filters.activo) p.set('activo', filters.activo === 'true')
      
      const data = await api('GET', `/usuarios?${p}`)
      setUsuarios(toList(data, ['items', 'usuarios', 'data'])) 
    }
    catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [])

  const seguir = async (uid2) => {
    if (!user) { toast('Inicia sesión primero', 'error'); return }
    try { 
      await api('POST', `/usuarios/${user.id}/sigue/${uid2}`, { 
        notificaciones: true
      }); 
      toast(`Sigues a ${uid2}`, 'success') 
    }
    catch (e) { toast(e.message, 'error') }
  }

  const f = (k) => (e) => setFilters(p => ({ ...p, [k]: e.target.value }))

  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <PageHeader title="Buscar usuarios" subtitle="Encuentra y sigue a otros usuarios de la red." />
      
      <Card style={{ padding: '16px 20px', marginBottom: 22, display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'flex-end' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <label style={{ marginBottom: 0 }}>Edad mín.</label>
          <input type="number" value={filters.edad_min} onChange={f('edad_min')} placeholder="18" style={{ width: 80 }} />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <label style={{ marginBottom: 0 }}>Edad máx.</label>
          <input type="number" value={filters.edad_max} onChange={f('edad_max')} placeholder="99" style={{ width: 80 }} />
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <label style={{ marginBottom: 0 }}>Estado</label>
          <select value={filters.activo} onChange={f('activo')} style={{ width: 100 }}>
            <option value="">Todos</option>
            <option value="true">Activos</option>
            <option value="false">Inactivos</option>
          </select>
        </div>
        <Btn onClick={load}>Filtrar</Btn>
        <Btn variant="outline" onClick={() => { setFilters({ edad_min: '', edad_max: '', activo: '' }); setTimeout(load, 50) }}>Limpiar</Btn>
      </Card>

      {loading && <Spinner />}
      {error && <Alert type="error">{error}</Alert>}
      {!loading && !error && usuarios.length === 0 && <Empty message="Sin usuarios encontrados" icon="◌" />}
      {!loading && !error && usuarios.length > 0 && (
        <Card style={{ overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead style={{ background: 'var(--off)' }}>
              <tr>{['ID','Nombre','Email','Edad',''].map(h => (
                <th key={h} style={{ padding: '10px 16px', textAlign: 'left', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text-xs)', borderBottom: '1.5px solid var(--border)' }}>{h}</th>
              ))}</tr>
            </thead>
            <tbody>
              {usuarios.map(u => (
                <tr key={u.id} style={{ borderBottom: '1px solid var(--border)' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--off)'}
                  onMouseLeave={e => e.currentTarget.style.background = ''}>
                  <td style={{ padding: '12px 16px', fontSize: 12, color: 'var(--text-xs)' }}>{u.id}</td>
                  <td style={{ padding: '12px 16px', fontWeight: 600 }}>{u.nombre || '-'}</td>
                  <td style={{ padding: '12px 16px', color: 'var(--text-xs)' }}>{u.email || '-'}</td>
                  <td style={{ padding: '12px 16px', color: 'var(--text-xs)' }}>{u.edad || '-'}</td>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', gap: 5 }}>
                      {user && user.id !== u.id && <Btn size="sm" variant="outline" onClick={() => seguir(u.id)}>Seguir</Btn>}
                      {!user && <Btn size="sm" variant="ghost" onClick={() => onLogin(u)}>Usar sesión</Btn>}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  )
}

function Section({ title, children, action }) {
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)', paddingBottom: 8, marginBottom: 12 }}>
        <h3 style={{ fontSize: 13, textTransform: 'uppercase', letterSpacing: '.1em', color: 'var(--text-xs)', fontWeight: 600, margin: 0 }}>{title}</h3>
        {action}
      </div>
      {children}
    </div>
  )
}
