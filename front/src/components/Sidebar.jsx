import { useState } from 'react'

const ADMIN_NAV = [
  { id: 'series', label: 'Catálogo', icon: '▤', section: 'Gestión' },
  { id: 'actores', label: 'Actores', icon: '◎', section: null },
  { id: 'csv', label: 'Carga CSV', icon: '↑', section: 'Sistema' },
  { id: 'consultas', label: 'Consultas', icon: '⌥', section: null },
]

const USER_NAV = [
  { id: 'explorar', label: 'Explorar', icon: '◈', section: 'Descubrir' },
  { id: 'recomendaciones', label: 'Recomendaciones', icon: '★', section: null },
  { id: 'perfil', label: 'Mi perfil', icon: '◉', section: 'Cuenta' },
  { id: 'usuarios', label: 'Buscar usuarios', icon: '◌', section: null },
]

export default function Sidebar({ currentPage, onNavigate, role, onRoleChange, user, onLogout }) {
  const nav = role === 'admin' ? ADMIN_NAV : USER_NAV

  return (
    <aside style={{
      width: 232, background: 'var(--g700)', display: 'flex',
      flexDirection: 'column', flexShrink: 0, height: '100vh', position: 'sticky', top: 0,
    }}>
      {/* Brand */}
      <div style={{ padding: '26px 22px 20px', borderBottom: '1px solid rgba(255,255,255,.06)' }}>
        <div style={{ fontFamily: 'Syne,sans-serif', fontWeight: 800, fontSize: 19, color: '#e3e8e4', letterSpacing: '-.02em' }}>
          SeriesGraph
        </div>
        <div style={{ fontSize: 10, color: 'var(--g400)', textTransform: 'uppercase', letterSpacing: '1.8px', marginTop: 3 }}>
          Neo4j · BD2
        </div>
      </div>

      {/* Role switcher */}
      <div style={{ margin: '14px 16px', display: 'flex', background: 'rgba(255,255,255,.06)', borderRadius: 10, padding: 3 }}>
        {['admin', 'usuario'].map(r => (
          <button key={r} onClick={() => onRoleChange(r)} style={{
            flex: 1, padding: '7px 0', textAlign: 'center',
            fontSize: 12, fontWeight: 600, letterSpacing: '.03em',
            fontFamily: 'DM Sans, sans-serif',
            color: role === r ? '#e3e8e4' : 'var(--g400)',
            background: role === r ? 'var(--g600)' : 'transparent',
            border: 'none', borderRadius: 8, cursor: 'pointer', transition: 'all .15s',
            textTransform: 'capitalize',
          }}>{r}</button>
        ))}
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, overflowY: 'auto', padding: '4px 0' }}>
        {nav.map((item, i) => {
          const prevItem = nav[i - 1]
          const showSection = item.section && item.section !== prevItem?.section
          return (
            <div key={item.id}>
              {showSection && (
                <div style={{ padding: '12px 22px 4px', fontSize: 10, textTransform: 'uppercase', letterSpacing: '1.8px', color: 'var(--g500)', fontWeight: 600 }}>
                  {item.section}
                </div>
              )}
              <button
                onClick={() => onNavigate(item.id)}
                style={{
                  width: '100%', display: 'flex', alignItems: 'center', gap: 10,
                  padding: '9px 22px', border: 'none', borderLeft: currentPage === item.id ? '2px solid var(--g300)' : '2px solid transparent',
                  background: currentPage === item.id ? 'rgba(155,171,159,.12)' : 'transparent',
                  color: currentPage === item.id ? '#e3e8e4' : 'var(--g300)',
                  fontSize: 13.5, fontFamily: 'DM Sans, sans-serif', fontWeight: currentPage === item.id ? 500 : 400,
                  cursor: 'pointer', transition: 'all .15s', textAlign: 'left',
                }}>
                <span style={{ fontSize: 15, opacity: .8 }}>{item.icon}</span>
                {item.label}
              </button>
            </div>
          )
        })}
      </nav>

      {/* User footer */}
      <div style={{ padding: '14px 22px', borderTop: '1px solid rgba(255,255,255,.06)' }}>
        {user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              width: 34, height: 34, borderRadius: '50%', background: 'var(--g500)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 13, fontWeight: 700, color: 'var(--g100)', flexShrink: 0,
            }}>
              {(user.nombre || 'U').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13, color: 'var(--g200)', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {user.nombre || user.id}
              </div>
              <div style={{ fontSize: 10.5, color: 'var(--g500)', marginTop: 1 }}>{user.id}</div>
            </div>
            <button onClick={onLogout} style={{ background: 'none', border: 'none', color: 'var(--g400)', cursor: 'pointer', fontSize: 16 }} title="Cerrar sesión">→</button>
          </div>
        ) : (
          <div style={{ fontSize: 12, color: 'var(--g500)', lineHeight: 1.6 }}>
            Sin sesión activa.{' '}
            <span onClick={() => onNavigate('perfil')} style={{ color: 'var(--g300)', cursor: 'pointer' }}>
              Iniciar sesión →
            </span>
          </div>
        )}
      </div>
    </aside>
  )
}
