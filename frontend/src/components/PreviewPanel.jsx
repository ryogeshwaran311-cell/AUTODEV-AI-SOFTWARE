import React, { useState, useEffect } from 'react'
import { 
  Play, Square, RefreshCw, ExternalLink, Smartphone, 
  Tablet, Monitor, AlertTriangle, CheckCircle, Server, Activity, ShieldCheck
} from 'lucide-react'

export default function PreviewPanel({ project }) {
  const [device, setDevice] = useState('desktop') // desktop, tablet, mobile
  const [previewState, setPreviewState] = useState(project?.preview_url ? 'running' : 'idle') // idle, starting, running, error
  const [previewUrl, setPreviewUrl] = useState(project?.preview_url || null)
  const [serverInfo, setServerInfo] = useState(null)
  const [iframeKey, setIframeKey] = useState(Date.now())
  const [errorMessage, setErrorMessage] = useState('')

  // Poll preview status
  const checkStatus = async () => {
    if (!project?.id) return
    try {
      const res = await fetch(`/api/projects/${project.id}/preview/status`)
      const data = await res.json()
      if (data.success && data.preview) {
        setServerInfo(data.preview)
        if (data.preview.status === 'RUNNING' && data.preview.preview_url) {
          setPreviewUrl(data.preview.preview_url)
          setPreviewState('running')
        }
      }
    } catch (e) {
      console.warn('Status check warning:', e)
    }
  }

  // Auto-start preview if project is READY and preview is not yet running
  useEffect(() => {
    checkStatus()
    if (project?.id && (project.status === 'READY' || project.preview_url) && previewState === 'idle') {
      handleStart()
    }
    const interval = setInterval(checkStatus, 2500)
    return () => clearInterval(interval)
  }, [project?.id, project?.status])

  const handleStart = async () => {
    if (!project?.id) return
    setPreviewState('starting')
    setErrorMessage('')
    try {
      const res = await fetch(`/api/projects/${project.id}/preview/start`, { method: 'POST' })
      const data = await res.json()
      if (data.success) {
        setPreviewUrl(data.preview_url)
        setPreviewState('running')
        setIframeKey(Date.now())
      } else {
        setPreviewState('error')
        setErrorMessage(data.error || 'Failed to start development servers')
      }
    } catch (err) {
      setPreviewState('error')
      setErrorMessage(err.message)
    }
  }

  const handleStop = async () => {
    if (!project?.id) return
    try {
      await fetch(`/api/projects/${project.id}/preview/stop`, { method: 'POST' })
      setPreviewState('idle')
      setPreviewUrl(null)
    } catch (e) {
      console.error(e)
    }
  }

  const handleReload = () => {
    setIframeKey(Date.now())
  }

  const deviceWidths = {
    desktop: '100%',
    tablet: '768px',
    mobile: '375px'
  }

  return (
    <div className="glass-panel" style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', minHeight: '680px' }}>
      {/* Preview Navigation Toolbar */}
      <div style={{
        padding: '0.85rem 1.5rem',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'rgba(0, 0, 0, 0.3)',
        flexWrap: 'wrap',
        gap: '0.75rem'
      }}>
        {/* Left: Device Frame Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', background: 'rgba(255, 255, 255, 0.05)', padding: '0.2rem', borderRadius: 'var(--radius-md)' }}>
          <button
            className={`btn btn-sm ${device === 'desktop' ? 'btn-primary' : ''}`}
            style={{ padding: '0.35rem 0.6rem', border: 'none', background: device === 'desktop' ? 'var(--accent-indigo)' : 'transparent' }}
            onClick={() => setDevice('desktop')}
            title="Desktop View"
          >
            <Monitor size={15} />
          </button>
          <button
            className={`btn btn-sm ${device === 'tablet' ? 'btn-primary' : ''}`}
            style={{ padding: '0.35rem 0.6rem', border: 'none', background: device === 'tablet' ? 'var(--accent-indigo)' : 'transparent' }}
            onClick={() => setDevice('tablet')}
            title="Tablet View (768px)"
          >
            <Tablet size={15} />
          </button>
          <button
            className={`btn btn-sm ${device === 'mobile' ? 'btn-primary' : ''}`}
            style={{ padding: '0.35rem 0.6rem', border: 'none', background: device === 'mobile' ? 'var(--accent-indigo)' : 'transparent' }}
            onClick={() => setDevice('mobile')}
            title="Mobile View (375px)"
          >
            <Smartphone size={15} />
          </button>
        </div>

        {/* Center: Fake Browser Address Bar */}
        <div style={{
          flex: 1,
          maxWidth: '520px',
          background: 'rgba(0, 0, 0, 0.5)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-full)',
          padding: '0.35rem 1rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          fontSize: '0.8rem',
          fontFamily: 'var(--font-mono)',
          color: 'var(--text-secondary)'
        }}>
          <Server size={14} color="var(--accent-indigo)" />
          <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {previewUrl || `http://localhost:${serverInfo?.frontend_port || 5200}`}
          </span>
          {previewState === 'running' && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--accent-emerald)', boxShadow: '0 0 8px var(--accent-emerald)' }}></span>
              <span style={{ fontSize: '0.7rem', color: 'var(--accent-emerald)', fontWeight: 600 }}>0.0.0.0 (LIVE)</span>
            </div>
          )}
        </div>

        {/* Right: Server Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {previewState === 'running' ? (
            <>
              <button className="btn btn-secondary btn-sm" onClick={handleReload} title="Reload Preview Frame">
                <RefreshCw size={14} />
              </button>
              <a
                href={previewUrl}
                target="_blank"
                rel="noreferrer"
                className="btn btn-secondary btn-sm"
                title="Open in new browser tab"
              >
                <ExternalLink size={14} />
              </a>
              <button className="btn btn-secondary btn-sm" onClick={handleStop} style={{ color: 'var(--accent-rose)' }}>
                <Square size={13} />
                <span>Stop</span>
              </button>
            </>
          ) : (
            <button
              className="btn btn-emerald btn-sm"
              onClick={handleStart}
              disabled={previewState === 'starting'}
            >
              <Play size={14} />
              <span>{previewState === 'starting' ? 'Starting Server...' : 'Start Preview'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Frame Container */}
      <div style={{
        flex: 1,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        background: '#04060a',
        padding: device === 'desktop' ? '0' : '1.5rem',
        overflow: 'auto',
        position: 'relative'
      }}>
        {previewState === 'running' && previewUrl ? (
          <iframe
            key={iframeKey}
            src={previewUrl}
            title={`${project?.name || 'Generated Application'} Preview`}
            style={{
              width: deviceWidths[device],
              height: '650px',
              border: device === 'desktop' ? 'none' : '1px solid var(--border-medium)',
              borderRadius: device === 'desktop' ? '0' : 'var(--radius-lg)',
              background: '#0b0f19',
              boxShadow: device === 'desktop' ? 'none' : '0 20px 50px rgba(0,0,0,0.8)',
              transition: 'width 0.3s ease'
            }}
          />
        ) : previewState === 'starting' ? (
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <div className="spinner" style={{
              width: '42px',
              height: '42px',
              border: '3px solid rgba(99, 102, 241, 0.2)',
              borderTopColor: 'var(--accent-indigo)',
              borderRadius: '50%',
              margin: '0 auto 1.5rem',
              animation: 'spinSlow 1s linear infinite'
            }}></div>
            <h4 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.5rem' }}>
              Bootstrapping Full-Stack Preview Environment
            </h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', maxWidth: '440px', margin: '0 auto' }}>
              Linking dependencies, binding servers to 0.0.0.0, and synchronizing REST API endpoints...
            </p>
          </div>
        ) : previewState === 'error' ? (
          <div style={{ textAlign: 'center', padding: '3rem', maxWidth: '480px' }}>
            <AlertTriangle size={36} color="var(--accent-rose)" style={{ marginBottom: '1rem' }} />
            <h4 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--accent-rose)', marginBottom: '0.5rem' }}>
              Preview Server Failed to Start
            </h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
              {errorMessage || 'Unable to bind to local port or start subprocess.'}
            </p>
            <button className="btn btn-primary btn-sm" onClick={handleStart}>
              Retry Preview Startup
            </button>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <div style={{
              width: '64px',
              height: '64px',
              borderRadius: '20px',
              background: 'rgba(99, 102, 241, 0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.25rem',
              color: 'var(--accent-indigo)'
            }}>
              <Play size={28} />
            </div>
            <h4 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>
              Live Embedded Preview
            </h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', maxWidth: '420px', margin: '0 auto 1.5rem' }}>
              Launch the generated full-stack application (Python Flask + React Vite + SQLite DB) in an isolated process sandbox.
            </p>
            <button className="btn btn-emerald btn-lg" onClick={handleStart}>
              <Play size={18} />
              <span>Launch Live Preview</span>
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
