import React from 'react'
import { LayoutDashboard, Layers, BarChart3, Settings, Shield } from 'lucide-react'

export default function Sidebar({ activeTab, setActiveTab }) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'records', label: 'Manage Records', icon: Layers },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: Settings },
  ]

  return (
    <aside style={{
      width: '240px',
      borderRight: '1px solid var(--border-color)',
      background: 'rgba(17, 24, 39, 0.6)',
      display: 'flex',
      flexDirection: 'column',
      padding: '1.5rem 1rem',
      flexShrink: 0
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0 0.5rem 1.5rem 0.5rem', borderBottom: '1px solid var(--border-color)' }}>
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '10px',
          background: 'var(--accent-gradient)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff'
        }}>
          <Shield size={20} />
        </div>
        <div>
          <h3 style={{ fontSize: '0.95rem', fontWeight: 700 }}>AutoDev App</h3>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>v1.0 Production</p>
        </div>
      </div>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', marginTop: '1.5rem', flex: 1 }}>
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = activeTab === item.id
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: '0.75rem 1rem',
                borderRadius: 'var(--radius-md)',
                border: 'none',
                background: isActive ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                color: isActive ? 'var(--accent-primary)' : 'var(--text-secondary)',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.875rem',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.2s ease',
                borderLeft: isActive ? '3px solid var(--accent-primary)' : '3px solid transparent'
              }}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          )
        })}
      </nav>

      <div style={{
        padding: '1rem',
        borderRadius: 'var(--radius-md)',
        background: 'rgba(0, 0, 0, 0.25)',
        border: '1px solid var(--border-color)',
        fontSize: '0.75rem',
        color: 'var(--text-muted)'
      }}>
        <p style={{ fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>AutoDevAI Engine</p>
        <p>Zero-configuration full-stack deployment ready.</p>
      </div>
    </aside>
  )
}