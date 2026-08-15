import React, { useState, useEffect } from 'react'
import confetti from 'canvas-confetti'
import { Sparkles, Terminal, Code, Cpu, Github, CheckCircle2, Shield } from 'lucide-react'
import ProjectInput from './components/ProjectInput'
import AgentPipeline from './components/AgentPipeline'
import ActionToolbar from './components/ActionToolbar'
import PreviewPanel from './components/PreviewPanel'
import DeployModal from './components/DeployModal'
import ApiKeyModal from './components/ApiKeyModal'
import ProjectHistory from './components/ProjectHistory'
import CodeExplorer from './components/CodeExplorer'

export default function App() {
  const [prompt, setPrompt] = useState('')
  const [activeProject, setActiveProject] = useState(null)
  const [projectsList, setProjectsList] = useState([])
  const [logs, setLogs] = useState([])
  const [generating, setGenerating] = useState(false)
  const [activeView, setActiveView] = useState('pipeline') // pipeline, preview, code
  const [downloading, setDownloading] = useState(false)

  // Modals
  const [isDeployOpen, setIsDeployOpen] = useState(false)
  const [isApiKeyOpen, setIsApiKeyOpen] = useState(false)
  const [isHistoryOpen, setIsHistoryOpen] = useState(false)
  const [geminiConfig, setGeminiConfig] = useState(null)

  // Fetch initial config & project list
  const fetchConfigAndProjects = async () => {
    try {
      const cfgRes = await fetch('/api/config')
      const cfgData = await cfgRes.json()
      setGeminiConfig(cfgData)

      const projRes = await fetch('/api/projects')
      const projData = await projRes.json()
      if (projData.success && projData.projects) {
        setProjectsList(projData.projects)
        if (projData.projects.length > 0 && !activeProject) {
          loadProjectDetails(projData.projects[0].id)
        }
      }
    } catch (err) {
      console.warn('Initial load warning:', err)
    }
  }

  useEffect(() => {
    fetchConfigAndProjects()
  }, [])

  // Load single project details
  const loadProjectDetails = async (projectId) => {
    try {
      const res = await fetch(`/api/projects/${projectId}`)
      const data = await res.json()
      if (data.success) {
        setActiveProject(data.project)
        // Also fetch logs
        const statusRes = await fetch(`/api/projects/${projectId}/status`)
        const statusData = await statusRes.json()
        if (statusData.success) {
          setLogs(statusData.logs || [])
        }
      }
    } catch (e) {
      console.error(e)
    }
  }

  const [directDeployRequested, setDirectDeployRequested] = useState(false)

  // Poll active project while running
  useEffect(() => {
    if (!activeProject?.id || activeProject.status === 'READY' || activeProject.status === 'FAILED') {
      return
    }

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/projects/${activeProject.id}/status`)
        const data = await res.json()
        if (data.success) {
          setActiveProject(prev => ({
            ...prev,
            status: data.status,
            current_stage: data.current_stage,
            progress_pct: data.progress_pct,
            preview_url: data.preview_url
          }))
          setLogs(data.logs || [])

          if (data.status === 'READY') {
            setGenerating(false)
            // Trigger celebration confetti
            try {
              confetti({ particleCount: 120, spread: 80, origin: { y: 0.6 } })
            } catch (e) {}

            // Auto-switch to live preview or open unified deploy modal
            if (directDeployRequested) {
              setIsDeployOpen(true)
              setDirectDeployRequested(false)
            } else {
              setActiveView('preview')
            }

            // Refresh project list
            fetchConfigAndProjects()
          } else if (data.status === 'FAILED') {
            setGenerating(false)
          }
        }
      } catch (err) {
        console.error('Polling error:', err)
      }
    }, 1500)

    return () => clearInterval(interval)
  }, [activeProject?.id, activeProject?.status, directDeployRequested])

  // Handle Project Generation
  const handleGenerate = async (promptText, directDeploy = false) => {
    setGenerating(true)
    setLogs([])
    setDirectDeployRequested(directDeploy)
    setActiveView('pipeline')

    try {
      const res = await fetch('/api/projects/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: promptText })
      })
      const data = await res.json()
      if (data.success) {
        setActiveProject({
          id: data.project_id,
          name: 'Generating Application...',
          slug: data.slug,
          prompt: promptText,
          status: 'RUNNING',
          current_stage: 'requirement',
          progress_pct: 5
        })
      } else {
        alert(`Generation request failed: ${data.error}`)
        setGenerating(false)
      }
    } catch (err) {
      alert(`Network error: ${err.message}`)
      setGenerating(false)
    }
  }

  // Handle ZIP Download
  const handleDownloadZip = async () => {
    if (!activeProject?.id) return
    setDownloading(true)
    try {
      window.location.href = `/api/projects/${activeProject.id}/download`
    } catch (err) {
      console.error(err)
    } finally {
      setTimeout(() => setDownloading(false), 2000)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', position: 'relative', zIndex: 1 }}>
      {/* Top Navigation Bar */}
      <header style={{
        height: '70px',
        borderBottom: '1px solid var(--border-subtle)',
        background: 'rgba(7, 9, 14, 0.85)',
        backdropFilter: 'blur(16px)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 2rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '12px',
            background: 'var(--grad-primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: 'var(--shadow-glow)'
          }}>
            <Cpu size={22} color="#fff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1.1 }}>
              AutoDev<span style={{ color: 'var(--accent-indigo)' }}>AI</span>
            </h1>
            <p style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
              Autonomous Multi-Agent Software Engineer
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div className="badge badge-completed" style={{ gap: '0.4rem', padding: '0.35rem 0.75rem' }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'currentColor' }}></span>
            <span>Gemini Engine Ready</span>
          </div>

          <button
            className="btn btn-secondary btn-sm"
            onClick={() => setIsApiKeyOpen(true)}
          >
            <Sparkles size={14} color="var(--accent-indigo)" />
            <span>AI Settings</span>
          </button>
        </div>
      </header>

      {/* Main Container */}
      <main style={{ flex: 1, padding: '2rem 1.5rem', maxWidth: '1440px', width: '100%', margin: '0 auto' }}>
        {/* Top: Project Idea Input */}
        <ProjectInput
          prompt={prompt}
          setPrompt={setPrompt}
          onGenerate={handleGenerate}
          generating={generating}
          geminiConfig={geminiConfig}
          onOpenApiKeyModal={() => setIsApiKeyOpen(true)}
        />

        {/* Middle: Action Toolbar with 3 active controls: Preview, Deploy, ZIP */}
        <ActionToolbar
          project={activeProject}
          activeView={activeView}
          setActiveView={setActiveView}
          onOpenDeploy={() => setIsDeployOpen(true)}
          onDownloadZip={handleDownloadZip}
          onToggleHistory={() => setIsHistoryOpen(true)}
          downloading={downloading}
        />

        {/* View 1: Agent Pipeline & Real-Time Event Stream */}
        {activeView === 'pipeline' && (
          <AgentPipeline project={activeProject} logs={logs} />
        )}

        {/* View 2: Live Embedded Preview Frame */}
        {activeView === 'preview' && (
          <PreviewPanel project={activeProject} />
        )}

        {/* View 3: Source Code Explorer */}
        {activeView === 'code' && (
          <CodeExplorer project={activeProject} />
        )}
      </main>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--border-subtle)',
        padding: '1.25rem 2rem',
        textAlign: 'center',
        fontSize: '0.8rem',
        color: 'var(--text-muted)',
        background: 'rgba(7, 9, 14, 0.95)'
      }}>
        AutoDevAI – Autonomous Multi-Agent Full-Stack Software Engineering Platform powered by Google Gemini.
      </footer>

      {/* Modals & Drawers */}
      <DeployModal
        isOpen={isDeployOpen}
        onClose={() => setIsDeployOpen(false)}
        project={activeProject}
      />

      <ApiKeyModal
        isOpen={isApiKeyOpen}
        onClose={() => setIsApiKeyOpen(false)}
        currentConfig={geminiConfig}
        onSaveConfig={(updated) => setGeminiConfig(updated)}
      />

      <ProjectHistory
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        projects={projectsList}
        activeProjectId={activeProject?.id}
        onSelectProject={(id) => { loadProjectDetails(id); setActiveView('pipeline'); }}
      />
    </div>
  )
}
