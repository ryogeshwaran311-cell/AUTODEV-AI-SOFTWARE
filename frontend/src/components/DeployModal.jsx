import React, { useState } from 'react'
import { X, Rocket, CheckCircle2, AlertCircle, ExternalLink, ShieldCheck, Key, Layers, Server, Globe, Cpu } from 'lucide-react'

export default function DeployModal({ isOpen, onClose, project }) {
  const [token, setToken] = useState('')
  const [deploying, setDeploying] = useState(false)
  const [deployResult, setDeployResult] = useState(null)

  if (!isOpen) return null

  const handleDeploy = async (e) => {
    e.preventDefault()
    if (!project?.id) return
    setDeploying(true)
    setDeployResult(null)

    try {
      const res = await fetch(`/api/projects/${project.id}/deploy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target: 'render',
          credentials: {
            render_api_key: token.trim() || undefined
          }
        })
      })
      const data = await res.json()
      setDeployResult(data)
    } catch (err) {
      setDeployResult({
        success: false,
        status: 'FAILED',
        error: err.message
      })
    } finally {
      setDeploying(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '580px' }}>
        {/* Header */}
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '12px', background: 'var(--grad-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', boxShadow: 'var(--shadow-glow)' }}>
              <Rocket size={22} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800 }}>Deploy Full-Stack Application</h3>
                <span className="badge badge-completed" style={{ fontSize: '0.7rem' }}>Render Blueprint</span>
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Deploy merged React UI + Flask API + SQLite DB on a single production URL
              </p>
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleDeploy} style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {/* Architecture Overview Card */}
          <div style={{
            background: 'rgba(99, 102, 241, 0.08)',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            borderRadius: 'var(--radius-lg)',
            padding: '1.2rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.75rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, color: '#fff', fontSize: '0.9rem' }}>
              <ShieldCheck size={18} color="var(--accent-emerald)" />
              <span>Native 1-Click Render Architecture</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.8rem' }}>
              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.6rem 0.8rem', borderRadius: 'var(--radius-md)' }}>
                <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.7rem' }}>Frontend (Client SPA)</span>
                <strong style={{ color: 'var(--accent-cyan)' }}>React 18 + Pure CSS</strong>
              </div>
              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.6rem 0.8rem', borderRadius: 'var(--radius-md)' }}>
                <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.7rem' }}>Backend (REST API)</span>
                <strong style={{ color: 'var(--accent-indigo)' }}>Python Flask + SQLite</strong>
              </div>
            </div>
            <p style={{ fontSize: '0.775rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.4 }}>
              Uses root <code style={{ color: '#fff' }}>render.yaml</code> Blueprint. Serves the React frontend on <code style={{ color: '#fff' }}>/</code> (with catch-all to <code style={{ color: '#fff' }}>index.html</code>) and all REST endpoints on <code style={{ color: '#fff' }}>/api/*</code>.
            </p>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.4rem' }}>
              Render API Key (Optional for Automatic Direct Sync)
            </label>
            <input
              type="password"
              className="form-input"
              placeholder="e.g. rnd_..."
              value={token}
              onChange={(e) => setToken(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                background: 'rgba(0,0,0,0.3)',
                border: '1px solid var(--border-medium)',
                borderRadius: 'var(--radius-md)',
                color: '#fff',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.85rem'
              }}
            />
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
              If provided, AutoDevAI automatically synchronizes with Render API without manual steps.
            </p>
          </div>

          {/* Deployment Results Output */}
          {deployResult && (
            <div style={{
              padding: '1rem',
              borderRadius: 'var(--radius-md)',
              background: deployResult.success ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)',
              border: `1px solid ${deployResult.success ? 'rgba(16, 185, 129, 0.3)' : 'rgba(244, 63, 94, 0.3)'}`,
              fontSize: '0.85rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', fontWeight: 600 }}>
                {deployResult.success ? (
                  <>
                    <CheckCircle2 size={16} color="var(--accent-emerald)" />
                    <span style={{ color: 'var(--accent-emerald)' }}>Full-Stack Deployment Configured</span>
                  </>
                ) : (
                  <>
                    <AlertCircle size={16} color="var(--accent-rose)" />
                    <span style={{ color: 'var(--accent-rose)' }}>Deployment Notice</span>
                  </>
                )}
              </div>
              <p style={{ color: 'var(--text-secondary)', marginBottom: deployResult.setup_instructions ? '0.75rem' : '0' }}>
                {deployResult.message || deployResult.error}
              </p>

              {deployResult.setup_instructions && (
                <ul style={{ paddingLeft: '1.2rem', color: 'var(--text-main)', fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                  {deployResult.setup_instructions.map((step, idx) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ul>
              )}

              {deployResult.url && (
                <a
                  href={deployResult.url}
                  target="_blank"
                  rel="noreferrer"
                  className="btn btn-sm btn-primary"
                  style={{ marginTop: '0.85rem', display: 'inline-flex', gap: '0.4rem' }}
                >
                  <ExternalLink size={14} /> Open Render Cloud Console
                </a>
              )}
            </div>
          )}

          {/* Action footer */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Close
            </button>
            <button type="submit" className="btn btn-primary" disabled={deploying} style={{ minWidth: '200px', fontWeight: 700 }}>
              {deploying ? 'Deploying...' : '🚀 Deploy Full-Stack App'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
