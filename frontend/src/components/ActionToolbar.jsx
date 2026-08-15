import React from 'react'
import { Eye, Rocket, Download, Code, History, FileText, CheckCircle2 } from 'lucide-react'

export default function ActionToolbar({
  project,
  activeView,
  setActiveView,
  onOpenDeploy,
  onDownloadZip,
  onToggleHistory,
  downloading
}) {
  const isReady = project && (project.status === 'READY' || project.progress_pct >= 80)

  return (
    <div className="glass-panel" style={{ padding: '1rem 1.5rem', marginTop: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
      {/* View Switchers */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
        <button
          className={`btn btn-sm ${activeView === 'pipeline' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveView('pipeline')}
        >
          <FileText size={15} />
          <span>Pipeline & Logs</span>
        </button>

        <button
          className={`btn btn-sm ${activeView === 'preview' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveView('preview')}
          disabled={!isReady}
        >
          <Eye size={15} />
          <span>👁️ Live Preview</span>
        </button>

        <button
          className={`btn btn-sm ${activeView === 'code' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveView('code')}
          disabled={!project?.project_path}
        >
          <Code size={15} />
          <span>Code Explorer</span>
        </button>

        <button
          className="btn btn-secondary btn-sm"
          onClick={onToggleHistory}
          title="View Generation History"
        >
          <History size={15} />
          <span>Project History</span>
        </button>
      </div>

      {/* Primary Operation Action Buttons */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <button
          className="btn btn-cyan btn-sm"
          onClick={onOpenDeploy}
          disabled={!isReady}
          title="Deploy to Vercel and Render"
        >
          <Rocket size={15} />
          <span>🚀 Deploy Project</span>
        </button>

        <button
          className="btn btn-emerald btn-sm"
          onClick={onDownloadZip}
          disabled={!isReady || downloading}
          title="Download Complete Source Code ZIP"
        >
          <Download size={15} />
          <span>{downloading ? 'Packing ZIP...' : '📦 Download ZIP'}</span>
        </button>
      </div>
    </div>
  )
}
