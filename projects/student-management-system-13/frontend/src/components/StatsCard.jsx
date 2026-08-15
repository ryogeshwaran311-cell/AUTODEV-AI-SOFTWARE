import React from 'react'
import { Layers, Database, ShieldCheck, Activity } from 'lucide-react'

const iconMap = {
  Layers,
  Database,
  ShieldCheck,
  Activity
}

export default function StatsCard({ title, value, subtitle, icon = 'Layers', color = 'indigo' }) {
  const IconComponent = iconMap[icon] || Layers

  const colorStyles = {
    indigo: { bg: 'rgba(99, 102, 241, 0.15)', text: '#a5b4fc', border: 'rgba(99, 102, 241, 0.3)' },
    emerald: { bg: 'rgba(16, 185, 129, 0.15)', text: '#6ee7b7', border: 'rgba(16, 185, 129, 0.3)' },
    amber: { bg: 'rgba(245, 158, 11, 0.15)', text: '#fcd34d', border: 'rgba(245, 158, 11, 0.3)' },
  }[color] || { bg: 'rgba(99, 102, 241, 0.15)', text: '#a5b4fc', border: 'rgba(99, 102, 241, 0.3)' }

  return (
    <div className="glass-card" style={{ padding: '1.25rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
      <div style={{
        width: '48px',
        height: '48px',
        borderRadius: '12px',
        background: colorStyles.bg,
        border: `1px solid ${colorStyles.border}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: colorStyles.text,
        flexShrink: 0
      }}>
        <IconComponent size={24} />
      </div>
      <div>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{title}</p>
        <h3 style={{ fontSize: '1.6rem', fontWeight: 800, margin: '0.15rem 0', fontFamily: 'var(--font-heading)' }}>{value}</h3>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{subtitle}</p>
      </div>
    </div>
  )
}