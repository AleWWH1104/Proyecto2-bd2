import { useState } from 'react'
import Sidebar from './components/Sidebar'
import { ToastContainer, toast } from './components/ui'
import AdminSeries from './pages/admin/Series'
import { AdminActores, AdminCSV, AdminConsultas } from './pages/admin/Other'
import { Explorar, Recomendaciones, Perfil, BuscarUsuarios } from './pages/usuario/Pages'
import './index.css'

export default function App() {
  const [role, setRole] = useState('admin')
  const [page, setPage] = useState('series')
  const [user, setUser] = useState(null)

  const handleRoleChange = (r) => {
    setRole(r)
    setPage(r === 'admin' ? 'series' : 'explorar')
  }

  const handleLogin = (u) => { setUser(u) }
  const handleLogout = () => { setUser(null); toast('Sesión cerrada') }
  const handleUpdate = (u) => setUser(u)

  const renderPage = () => {
    if (role === 'admin') {
      switch (page) {
        case 'series': return <AdminSeries />
        case 'actores': return <AdminActores />
        case 'csv': return <AdminCSV />
        case 'consultas': return <AdminConsultas />
        default: return <AdminSeries />
      }
    } else {
      switch (page) {
        case 'explorar': return <Explorar user={user} />
        case 'recomendaciones': return <Recomendaciones user={user} onNavigate={setPage} />
        case 'perfil': return <Perfil user={user} onLogin={handleLogin} onRegister={handleLogin} onLogout={handleLogout} onUpdate={handleUpdate} />
        case 'usuarios': return <BuscarUsuarios user={user} onLogin={handleLogin} />
        default: return <Explorar user={user} />
      }
    }
  }

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <Sidebar
        currentPage={page}
        onNavigate={setPage}
        role={role}
        onRoleChange={handleRoleChange}
        user={user}
        onLogout={handleLogout}
      />
      <main style={{ flex: 1, overflowY: 'auto', background: 'var(--off)' }}>
        {renderPage()}
      </main>
      <ToastContainer />
    </div>
  )
}
