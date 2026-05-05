import { useState, useEffect } from 'react'

/* ── BUTTON ── */
export function Btn({ children, variant = 'primary', size = 'md', onClick, style, type = 'button', disabled }) {
  const base = {
    display: 'inline-flex', alignItems: 'center', gap: 6,
    border: 'none', borderRadius: 10, fontFamily: 'inherit',
    fontWeight: 600, cursor: disabled ? 'not-allowed' : 'pointer',
    transition: 'all .15s', lineHeight: 1, opacity: disabled ? .5 : 1,
  }
  const sizes = { sm: { padding: '7px 14px', fontSize: 12.5 }, md: { padding: '11px 20px', fontSize: 14 }, lg: { padding: '14px 28px', fontSize: 15 } }
  const variants = {
    primary: { background: 'var(--g700)', color: '#e3e8e4' },
    outline: { background: 'transparent', border: '1.5px solid var(--border)', color: 'var(--text-md)' },
    ghost: { background: 'transparent', color: 'var(--text-sm)', padding: '7px 10px' },
    danger: { background: 'transparent', border: '1.5px solid #f5c6c3', color: 'var(--red)' },
    green: { background: 'var(--g500)', color: '#fff' },
  }
  return (
    <button type={type} disabled={disabled} onClick={onClick}
      style={{ ...base, ...sizes[size], ...variants[variant], ...style }}>
      {children}
    </button>
  )
}

/* ── CARD ── */
export function Card({ children, style, onClick, hover }) {
  const [hov, setHov] = useState(false)
  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        background: 'var(--white)', borderRadius: 'var(--radius)',
        border: '1.5px solid var(--border)',
        boxShadow: hov && hover ? 'var(--shadow-md)' : 'var(--shadow)',
        transform: hov && hover ? 'translateY(-3px)' : 'none',
        transition: 'all .2s', ...style,
      }}>
      {children}
    </div>
  )
}

/* ── BADGE ── */
export function Badge({ children, color = 'gray' }) {
  const colors = {
    gray: { bg: 'var(--g100)', text: 'var(--text-sm)' },
    green: { bg: 'var(--green-bg)', text: 'var(--green)' },
    blue: { bg: 'var(--blue-bg)', text: 'var(--blue)' },
    red: { bg: 'var(--red-bg)', text: 'var(--red)' },
    dark: { bg: 'var(--g700)', text: 'var(--g100)' },
  }
  const c = colors[color] || colors.gray
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center',
      padding: '3px 9px', borderRadius: 20,
      fontSize: 11.5, fontWeight: 600,
      background: c.bg, color: c.text, letterSpacing: '.02em',
    }}>{children}</span>
  )
}

/* ── RATING BAR ── */
export function RatingBar({ value }) {
  const v = parseFloat(value) || 0
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <div style={{ width: 56, height: 4, background: 'var(--g100)', borderRadius: 2, overflow: 'hidden' }}>
        <div style={{ width: `${v * 10}%`, height: '100%', background: 'var(--g500)', borderRadius: 2 }} />
      </div>
      <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-md)' }}>{v.toFixed(1)}</span>
    </div>
  )
}

/* ── STAT CARD ── */
export function StatCard({ label, value, sub, accent }) {
  return (
    <Card style={{ padding: '20px 24px' }}>
      <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '.1em', color: 'var(--text-xs)', fontWeight: 600 }}>{label}</div>
      <div style={{ fontFamily: 'Syne,sans-serif', fontSize: 32, fontWeight: 800, color: accent || 'var(--text)', marginTop: 4, lineHeight: 1 }}>{value}</div>
      {sub && <div style={{ fontSize: 12, color: 'var(--text-xs)', marginTop: 4 }}>{sub}</div>}
    </Card>
  )
}

/* ── SPINNER ── */
export function Spinner() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '32px 0', color: 'var(--text-xs)', fontSize: 13.5 }}>
      <div style={{
        width: 18, height: 18, border: '2.5px solid var(--g100)',
        borderTopColor: 'var(--g500)', borderRadius: '50%',
        animation: 'spin .7s linear infinite', flexShrink: 0,
      }} />
      Cargando...
      <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
    </div>
  )
}

/* ── EMPTY ── */
export function Empty({ message = 'Sin resultados', icon = '◌' }) {
  return (
    <div style={{ textAlign: 'center', padding: '60px 24px', color: 'var(--text-xs)' }}>
      <div style={{ fontSize: 36, marginBottom: 12, opacity: .4 }}>{icon}</div>
      <div style={{ fontSize: 14 }}>{message}</div>
    </div>
  )
}

/* ── ALERT ── */
export function Alert({ children, type = 'info' }) {
  const types = {
    info: { bg: 'var(--g50)', color: 'var(--text-sm)', border: 'var(--border)' },
    success: { bg: 'var(--green-bg)', color: 'var(--green)', border: '#b7dfc7' },
    error: { bg: 'var(--red-bg)', color: 'var(--red)', border: '#f5c6c3' },
  }
  const t = types[type]
  return (
    <div style={{
      padding: '11px 16px', borderRadius: 'var(--radius-sm)',
      fontSize: 13.5, background: t.bg, color: t.color,
      border: `1px solid ${t.border}`, marginBottom: 16,
    }}>{children}</div>
  )
}

/* ── FORM GROUP ── */
export function FG({ label, children, style }) {
  return (
    <div style={{ marginBottom: 14, ...style }}>
      {label && <label>{label}</label>}
      {children}
    </div>
  )
}

/* ── MODAL ── */
export function Modal({ title, children, onClose, wide }) {
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose?.() }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [onClose])

  return (
    <div onClick={(e) => e.target === e.currentTarget && onClose?.()}
      style={{
        position: 'fixed', inset: 0, background: 'rgba(24,30,24,.5)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        zIndex: 300, backdropFilter: 'blur(4px)',
      }}>
      <div style={{
        background: 'var(--white)', borderRadius: 18,
        width: wide ? 640 : 500, maxWidth: '95vw', maxHeight: '90vh',
        overflowY: 'auto', boxShadow: '0 24px 80px rgba(24,30,24,.2)',
      }}>
        <div style={{
          padding: '22px 28px 18px', borderBottom: '1.5px solid var(--border)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <h3 style={{ fontSize: 20 }}>{title}</h3>
          <button onClick={onClose} style={{
            background: 'var(--g100)', border: 'none', width: 30, height: 30,
            borderRadius: '50%', cursor: 'pointer', fontSize: 14,
            color: 'var(--text-sm)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>✕</button>
        </div>
        <div style={{ padding: '22px 28px' }}>{children}</div>
      </div>
    </div>
  )
}

/* ── MODAL FOOTER ── */
export function ModalFooter({ children }) {
  return (
    <div style={{
      display: 'flex', gap: 8, justifyContent: 'flex-end',
      marginTop: 22, paddingTop: 18, borderTop: '1.5px solid var(--border)',
    }}>{children}</div>
  )
}

/* ── SERIES CARD (big, lifestyle) ── */
// Pick a shade from the green palette based on the title
const GREEN_STOPS = [
  { bg: '#232a23', accent: '#9bab9f' }, // g700
  { bg: '#3a463e', accent: '#d0d7d2' }, // g600
  { bg: '#4c5951', accent: '#e3e8e4' }, // g500
  { bg: '#2d3d30', accent: '#9bab9f' }, // deep forest
  { bg: '#1e2b1e', accent: '#809385' }, // darkest
]

export function SerieCard({ serie, onClick }) {
  const [hov, setHov] = useState(false)
  const rating = parseFloat(serie.calificacion) || 0
  const idx = (serie.titulo?.charCodeAt(0) || 65) % GREEN_STOPS.length
  const { bg, accent } = GREEN_STOPS[idx]

  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        background: 'var(--white)', borderRadius: 'var(--radius)',
        border: hov ? '1.5px solid var(--g300)' : '1.5px solid var(--border)',
        overflow: 'hidden', cursor: onClick ? 'pointer' : 'default',
        transform: hov && onClick ? 'translateY(-3px)' : 'none',
        boxShadow: hov && onClick ? 'var(--shadow-md)' : 'var(--shadow)',
        transition: 'all .2s',
      }}>
      {/* Green palette header */}
      <div style={{
        height: 88,
        background: bg,
        display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between',
        padding: '14px 16px',
        position: 'relative', overflow: 'hidden',
      }}>
        {/* Decorative circle */}
        <div style={{
          position: 'absolute', right: -20, top: -20,
          width: 90, height: 90, borderRadius: '50%',
          background: accent, opacity: .08,
        }} />
        <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap', position: 'relative' }}>
          {(serie.estadoEmision === true || serie.estadoEmision === 'True') &&
            <span style={{ background: 'rgba(255,255,255,.15)', color: '#fff', fontSize: 10.5, fontWeight: 600, padding: '2px 8px', borderRadius: 20, letterSpacing: '.04em' }}>EN EMISIÓN</span>}
          {(serie.activa !== true && serie.activa !== 'True') &&
            <span style={{ background: 'rgba(0,0,0,.25)', color: 'rgba(255,255,255,.6)', fontSize: 10.5, fontWeight: 600, padding: '2px 8px', borderRadius: 20 }}>INACTIVA</span>}
        </div>
        {/* Rating chip */}
        <div style={{ background: 'rgba(0,0,0,.3)', backdropFilter: 'blur(4px)', borderRadius: 8, padding: '4px 9px', position: 'relative' }}>
          <span style={{ color: accent, fontSize: 13, fontWeight: 700 }}>★ {rating.toFixed(1)}</span>
        </div>
      </div>

      <div style={{ padding: '14px 16px 16px' }}>
        <div style={{ fontFamily: 'Syne,sans-serif', fontWeight: 700, fontSize: 15, lineHeight: 1.25, marginBottom: 5, color: 'var(--text)' }}>
          {serie.titulo}
        </div>
        <div style={{ fontSize: 12, color: 'var(--text-xs)', marginBottom: 9 }}>
          {serie.anio} · {serie.numTemporadas} temp. · {serie.numEpisodios} ep.
        </div>
        <div style={{
          fontSize: 12.5, color: 'var(--text-sm)', lineHeight: 1.5, marginBottom: 12,
          display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden',
        }}>
          {serie.sinopsis || 'Sin sinopsis disponible.'}
        </div>
        <div style={{ height: 3, background: 'var(--g100)', borderRadius: 2, overflow: 'hidden' }}>
          <div style={{ width: `${rating * 10}%`, height: '100%', background: bg, borderRadius: 2, transition: 'width .3s' }} />
        </div>
      </div>
    </div>
  )
}

/* ── PAGE HEADER ── */
export function PageHeader({ title, subtitle, action }) {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 28 }}>
      <div>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: 'var(--text)' }}>{title}</h1>
        {subtitle && <p style={{ fontSize: 13.5, color: 'var(--text-xs)', marginTop: 4 }}>{subtitle}</p>}
      </div>
      {action}
    </div>
  )
}

/* ── SECTION ── */
export function Section({ title, children, style }) {
  return (
    <div style={{ marginBottom: 32, ...style }}>
      {title && <h2 style={{ fontSize: 17, fontWeight: 700, marginBottom: 14, color: 'var(--text-md)' }}>{title}</h2>}
      {children}
    </div>
  )
}

/* ── TOAST (global) ── */
let _addToast = null
export function setToastFn(fn) { _addToast = fn }
export function toast(msg, type = 'info') { _addToast?.({ msg, type, id: Date.now() }) }

export function ToastContainer() {
  const [toasts, setToasts] = useState([])
  useEffect(() => {
    setToastFn((t) => {
      setToasts(prev => [...prev, t])
      setTimeout(() => setToasts(prev => prev.filter(x => x.id !== t.id)), 3200)
    })
  }, [])
  const colors = {
    success: ['var(--green-bg)', 'var(--green)', '#b7dfc7'],
    error: ['var(--red-bg)', 'var(--red)', '#f5c6c3'],
    info: ['var(--g50)', 'var(--text-sm)', 'var(--border)'],
  }
  return (
    <div style={{ position: 'fixed', bottom: 24, right: 24, zIndex: 999, display: 'flex', flexDirection: 'column', gap: 8 }}>
      {toasts.map(t => {
        const [bg, color, border] = colors[t.type] || colors.info
        return (
          <div key={t.id} style={{
            background: bg, color, border: `1px solid ${border}`,
            padding: '11px 18px', borderRadius: 10, fontSize: 13.5,
            boxShadow: 'var(--shadow-md)', maxWidth: 320, fontFamily: 'DM Sans,sans-serif',
          }}>{t.msg}</div>
        )
      })}
    </div>
  )
}