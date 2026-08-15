import React from 'react'
import { RefreshCw, Radio } from 'lucide-react'

export default function Navbar({ title, backendStatus, onRefresh }) {
  return (
    <header style={{
      height: '64px',
      borderBottom: '1px solid var(--border-color)',
      background: 'rgba(11, 15, 25, 0.8)',
      backdropFilter: 'blur(12px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 2rem',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '8px',
          background: 'var(--accent-gradient)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontWeight: 700,
          color: '#fff',
          fontSize: '0.85rem'
        }}>
          AI
        </div>
        <h2 style={{ fontSize: '1.1rem', fontWeight: 600 }}>{title || 'Create Calculator'}</h2>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
        <div className="badge badge-success" style={{ gap: '0.4rem' }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'currentColor' }}></span>
          {backendStatus === 'connected' ? 'Backend Online' : 'Active'}
        </div>

        <button 
          className="btn btn-secondary btn-sm"
          onClick={onRefresh}
          title="Refresh Data"
        >
          <RefreshCw size={14} />
          <span>Refresh</span>
        </button>
      </div>
    </header>
  )
}