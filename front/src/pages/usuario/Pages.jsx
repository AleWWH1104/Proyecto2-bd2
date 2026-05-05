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
    try { setResenas(toList(await api('GET', `/series/${s.id}/resenas`), ['resenas','data'])) } catch {}
  }

  const like = async () => { try { await api('POST', `/usuarios/${user.id}/le-gusta/${selected.id}`, { fecha: new Date().toISOString().split('T')[0], origen: 'explorar' }); toast('Guardado en likes ♥', 'success') } catch (e) { toast(e.message, 'error') } }
  const watchlist = async () => { try { await api('POST', `/usuarios/${user.id}/en-lista/${selected.id}`, { fechaAgregada: new Date().toISOString().split('T')[0], prioridad: 1, nota: '' }); toast('Agregada a watchlist', 'success') } catch (e) { toast(e.message, 'error') } }
  const vista = async () => { try { await api('POST', `/usuarios/${user.id}/vio/${selected.id}`, { fechaVisto: new Date().toISOString().split('T')[0], porcentajeVisto: 100.0, completada: true }); toast('Marcada como vista ✓', 'success') } catch (e) { toast(e.message, 'error') } }

  const crearResena = async () => {
    if (!user) { toast('Inicia sesión primero', 'error'); return }
    try {
      await api('POST', `/series/${selected.id}/resenas`, { ...formResena, calificacion: parseFloat(formResena.calificacion) || 8, contieneSpoilers: formResena.spoilers === 'true', usuarioId: user.id })
      toast('Reseña publicada', 'success'); setModalResena(false); setFormResena({})
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

          {user ? (
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 20 }}>
              <Btn size="sm" onClick={like}>♥ Me gusta</Btn>
              <Btn size="sm" variant="outline" onClick={watchlist}>+ Watchlist</Btn>
              <Btn size="sm" variant="outline" onClick={vista}>✓ Vista</Btn>
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
                  <div style={{ fontWeight: 600, fontSize: 13.5 }}>{r.titulo || 'Reseña'} <span style={{ color: 'var(--text-xs)', fontWeight: 400 }}>· {r.calificacion}/10</span></div>
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
            <FG label="Calificación (0–10)"><input type="number" step="0.5" min="0" max="10" value={formResena.calificacion || ''} onChange={e => setFormResena(p => ({ ...p, calificacion: e.target.value }))} /></FG>
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

  const load = async (withFilters = false) => {
    if (!user) return
    setLoading(true)
    try {
      const p = withFilters ? new URLSearchParams(Object.fromEntries(Object.entries(filters).filter(([, v]) => v))) : new URLSearchParams()
      setSeries(toList(await api('GET', `/recomendaciones/${user.id}?${p}`)))
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
        {[['rec','Personalizadas'],['filt','Con filtros']].map(([id, label]) => (
          <button key={id} onClick={() => { setTab(id); if (id === 'rec') load() }}
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
          <Btn onClick={() => load(true)}>Buscar</Btn>
        </Card>
      )}

      {loading && <Spinner />}
      {!loading && series.length === 0 && <Empty message="Sin recomendaciones disponibles" icon="★" />}
      {!loading && series.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(210px,1fr))', gap: 14 }}>
          {series.map(s => <SerieCard key={s.id} serie={s} onClick={() => setSelected(s)} />)}
        </div>
      )}

      {selected && (
        <Modal title={selected.titulo} onClose={() => setSelected(null)}>
          <p style={{ fontSize: 13.5, color: 'var(--text-xs)', lineHeight: 1.65, marginBottom: 14 }}>{selected.sinopsis || 'Sin sinopsis.'}</p>
          <RatingBar value={selected.calificacion} />
          <div style={{ fontSize: 13, color: 'var(--text-xs)', marginTop: 8 }}>{selected.anio} · {selected.numTemporadas} temp.</div>
          <ModalFooter><Btn variant="outline" onClick={() => setSelected(null)}>Cerrar</Btn></ModalFooter>
        </Modal>
      )}
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

  const doLogin = async () => {
    if (!loginId) { toast('Ingresa un ID', 'error'); return }
    try { const u = await api('GET', `/usuarios/${loginId}`); onLogin(u); toast(`Bienvenido, ${u.nombre || u.id}!`, 'success') }
    catch { toast('Usuario no encontrado', 'error') }
  }

  const doRegister = async () => {
    if (!regForm.nombre || !regForm.email) { toast('Nombre y email requeridos', 'error'); return }
    try {
      const u = await api('POST', '/usuarios', {
        ...regForm,
        generosPreferidos: (regForm.generos || '').split(',').map(x => x.trim()).filter(Boolean),
        fechaRegistro: new Date().toISOString().split('T')[0],
        activo: true, premium: false, pais: regForm.pais || 'Guatemala', idioma: regForm.idioma || 'es',
      })
      onRegister(u || regForm); toast('¡Cuenta creada!', 'success'); setModal(null)
    } catch (e) { toast(e.message, 'error') }
  }

  const doUpdate = async () => {
    const body = {}
    if (editForm.nombre) body.nombre = editForm.nombre
    if (editForm.pais) body.pais = editForm.pais
    if (editForm.generos) body.generosPreferidos = editForm.generos.split(',').map(x => x.trim()).filter(Boolean)
    try { await api('PATCH', `/usuarios/${user.id}`, body); onUpdate({ ...user, ...body }); toast('Perfil actualizado', 'success'); setModal(null) }
    catch (e) { toast(e.message, 'error') }
  }

  const doFollow = async () => {
    if (!followId) { toast('Ingresa un ID', 'error'); return }
    try { await api('POST', `/usuarios/${user.id}/sigue/${followId}`, { fechaSeguido: new Date().toISOString().split('T')[0], notificaciones: true, origen: 'perfil' }); toast(`Ahora sigues a ${followId}`, 'success'); setFollowId('') }
    catch (e) { toast(e.message, 'error') }
  }

  if (!user) return (
    <div style={{ padding: '28px 32px 48px' }}>
      <PageHeader title="Mi perfil" subtitle="Inicia sesión o crea una cuenta." />
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, maxWidth: 600 }}>
        <Card style={{ padding: '28px 28px' }}>
          <h3 style={{ fontSize: 17, marginBottom: 18 }}>Iniciar sesión</h3>
          <FG label="ID de usuario"><input value={loginId} onChange={e => setLoginId(e.target.value)} placeholder="usr_0001" onKeyDown={e => e.key === 'Enter' && doLogin()} /></FG>
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
            <FG label="País"><input value={regForm.pais || 'Guatemala'} onChange={e => setRegForm(p => ({ ...p, pais: e.target.value }))} /></FG>
            <FG label="Idioma"><input value={regForm.idioma || 'es'} onChange={e => setRegForm(p => ({ ...p, idioma: e.target.value }))} /></FG>
          </div>
          <FG label="Géneros favoritos (coma)"><input value={regForm.generos || ''} onChange={e => setRegForm(p => ({ ...p, generos: e.target.value }))} placeholder="Drama, Thriller" /></FG>
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
            <Btn variant="outline" onClick={() => { setEditForm({ nombre: user.nombre, pais: user.pais, generos: (user.generosPreferidos || []).join(', ') }); setModal('editar') }}>Editar perfil</Btn>
            <Btn variant="ghost" onClick={onLogout}>Cerrar sesión</Btn>
          </div>
        }
      />
      <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: 16 }}>
        {/* Profile card */}
        <Card style={{ padding: '28px 24px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', marginBottom: 22 }}>
            <div style={{ width: 72, height: 72, borderRadius: '50%', background: `hsl(${hue},25%,35%)`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, fontFamily: 'Syne,sans-serif', fontWeight: 800, color: '#fff', marginBottom: 14 }}>
              {initials}
            </div>
            <div style={{ fontFamily: 'Syne,sans-serif', fontWeight: 700, fontSize: 18 }}>{user.nombre || user.id}</div>
            <div style={{ fontSize: 12.5, color: 'var(--text-xs)', marginTop: 3 }}>{user.email || ''}</div>
            <div style={{ marginTop: 10 }}><Badge color={user.premium ? 'blue' : 'gray'}>{user.premium ? 'Premium' : 'Free'}</Badge></div>
          </div>
          <div style={{ borderTop: '1.5px solid var(--border)', paddingTop: 18 }}>
            {[['ID', user.id], ['País', user.pais || '-'], ['Idioma', user.idioma || '-'], ['Desde', user.fechaRegistro || '-']].map(([k, v]) => (
              <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--border)', fontSize: 13 }}>
                <span style={{ color: 'var(--text-xs)' }}>{k}</span>
                <span style={{ fontWeight: 500 }}>{v}</span>
              </div>
            ))}
          </div>
          {user.generosPreferidos?.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '.1em', color: 'var(--text-xs)', fontWeight: 600, marginBottom: 8 }}>Géneros</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
                {user.generosPreferidos.map(g => <Badge key={g} color="gray">{g}</Badge>)}
              </div>
            </div>
          )}
        </Card>
        {/* Right column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <Card style={{ padding: '20px 24px' }}>
            <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 14 }}>Seguir a usuario</h3>
            <div style={{ display: 'flex', gap: 10 }}>
              <input value={followId} onChange={e => setFollowId(e.target.value)} placeholder="ID del usuario" style={{ maxWidth: 240 }} onKeyDown={e => e.key === 'Enter' && doFollow()} />
              <Btn variant="outline" onClick={doFollow}>Seguir</Btn>
            </div>
          </Card>
          <Card style={{ padding: '20px 24px' }}>
            <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 14 }}>Acciones rápidas</h3>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {[['Recomendaciones', 'recomendaciones'], ['Explorar series', 'explorar'], ['Buscar usuarios', 'usuarios']].map(([label]) => (
                <Btn key={label} variant="outline" size="sm">{label} →</Btn>
              ))}
            </div>
          </Card>
        </div>
      </div>

      {modal === 'editar' && (
        <Modal title="Editar perfil" onClose={() => setModal(null)}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
            <FG label="Nombre"><input value={editForm.nombre || ''} onChange={e => setEditForm(p => ({ ...p, nombre: e.target.value }))} /></FG>
            <FG label="País"><input value={editForm.pais || ''} onChange={e => setEditForm(p => ({ ...p, pais: e.target.value }))} /></FG>
          </div>
          <FG label="Géneros (coma)"><input value={editForm.generos || ''} onChange={e => setEditForm(p => ({ ...p, generos: e.target.value }))} /></FG>
          <ModalFooter>
            <Btn variant="outline" onClick={() => setModal(null)}>Cancelar</Btn>
            <Btn onClick={doUpdate}>Guardar</Btn>
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
  const [query, setQuery] = useState('')
  const [usuarios, setUsuarios] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = async () => {
    setLoading(true); setError(null)
    try { setUsuarios(toList(await api('GET', `/usuarios${query ? '?q=' + encodeURIComponent(query) : ''}`), ['usuarios', 'data'])) }
    catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [])

  const seguir = async (uid2) => {
    if (!user) { toast('Inicia sesión primero', 'error'); return }
    try { await api('POST', `/usuarios/${user.id}/sigue/${uid2}`, { fechaSeguido: new Date().toISOString().split('T')[0], notificaciones: true, origen: 'busqueda' }); toast(`Sigues a ${uid2}`, 'success') }
    catch (e) { toast(e.message, 'error') }
  }

  return (
    <div style={{ padding: '28px 32px 48px' }}>
      <PageHeader title="Buscar usuarios" subtitle="Encuentra y sigue a otros usuarios de la red." />
      <Card style={{ padding: '16px 20px', marginBottom: 22, display: 'flex', gap: 10, alignItems: 'flex-end' }}>
        <div style={{ flex: 1 }}>
          <label style={{ marginBottom: 4 }}>Nombre o email</label>
          <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Buscar…" onKeyDown={e => e.key === 'Enter' && load()} />
        </div>
        <Btn onClick={load}>Buscar</Btn>
      </Card>

      {loading && <Spinner />}
      {error && <Alert type="error">{error}</Alert>}
      {!loading && !error && usuarios.length === 0 && <Empty message="Sin usuarios encontrados" icon="◌" />}
      {!loading && !error && usuarios.length > 0 && (
        <Card style={{ overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead style={{ background: 'var(--off)' }}>
              <tr>{['Nombre','Email','País',''].map(h => (
                <th key={h} style={{ padding: '10px 16px', textAlign: 'left', fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.08em', color: 'var(--text-xs)', borderBottom: '1.5px solid var(--border)' }}>{h}</th>
              ))}</tr>
            </thead>
            <tbody>
              {usuarios.map(u => (
                <tr key={u.id} style={{ borderBottom: '1px solid var(--border)' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--off)'}
                  onMouseLeave={e => e.currentTarget.style.background = ''}>
                  <td style={{ padding: '12px 16px', fontWeight: 600 }}>{u.nombre || u.name || '-'}</td>
                  <td style={{ padding: '12px 16px', color: 'var(--text-xs)' }}>{u.email || '-'}</td>
                  <td style={{ padding: '12px 16px', color: 'var(--text-xs)' }}>{u.pais || '-'}</td>
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
