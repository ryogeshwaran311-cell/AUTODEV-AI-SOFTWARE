import React from 'react'
import { X, Clock, Layers, CheckCircle2, AlertCircle, ArrowRight } from 'lucide-react'

export default function ProjectHistory({ isOpen, onClose, projects = [], onSelectProject, activeProjectId }) {
  if (!isOpen) return null

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '650px' }}>
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Generated Applications History</h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Switch between previously engineered full-stack projects</p>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        <div style={{ maxHeight: '450px', overflowY: 'auto', padding: '1.25rem' }}>
          {projects.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '2rem' }}>
              No projects found in internal database.
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {projects.map((proj) => {
                const isActive = proj.id === activeProjectId
                return (
                  <div
                    key={proj.id}
                    className="glass-card"
                    style={{
                      padding: '1rem',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      borderColor: isActive ? 'var(--accent-indigo)' : 'var(--border-subtle)',
                      background: isActive ? 'rgba(99, 102, 241, 0.1)' : undefined
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                        <h4 style={{ fontSize: '0.95rem', fontWeight: 600 }}>{proj.name}</h4>
                        <span className={`badge ${
                          proj.status === 'READY' ? 'badge-completed' :
                          proj.status === 'FAILED' ? 'badge-failed' : 'badge-running'
                        }`}>
                          {proj.status}
                        </span>
                      </div>
                      <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', maxWidth: '380px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {proj.prompt}
                      </p>
                      <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem', marginTop: '0.25rem' }}>
                        <Clock size={11} /> {new Date(proj.created_at).toLocaleString()}
                      </span>
                    </div>

                    <button
                      className={`btn btn-sm ${isActive ? 'btn-primary' : 'btn-secondary'}`}
                      onClick={() => { onSelectProject(proj.id); onClose(); }}
                    >
                      <span>{isActive ? 'Current' : 'Load Project'}</span>
                      <ArrowRight size={13} />
                    </button>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
