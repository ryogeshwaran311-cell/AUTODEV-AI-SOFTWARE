import React, { useState, useEffect, useRef } from 'react'
import { 
  FileSearch, Compass, Code2, Database, CheckSquare, 
  Wrench, BookOpen, ShieldCheck, CheckCircle2, AlertCircle, 
  Terminal, ChevronDown, ChevronUp, Clock, Info
} from 'lucide-react'

export default function AgentPipeline({ project, logs = [] }) {
  const [showLogs, setShowLogs] = useState(true)
  const [selectedTab, setSelectedTab] = useState('overview')
  const logsEndRef = useRef(null)

  const stages = [
    { id: 'requirement', name: 'Requirement', icon: FileSearch, desc: 'Analyze idea & extract roles, entities' },
    { id: 'planning', name: 'Planning', icon: Compass, desc: 'Architect DB schema, REST routes & UI' },
    { id: 'coding', name: 'Coding', icon: Code2, desc: 'Generate complete full-stack source code' },
    { id: 'database', name: 'Database', icon: Database, desc: 'Setup workspace & SQLite models' },
    { id: 'testing', name: 'Testing', icon: CheckSquare, desc: 'AST syntax, dependencies & QA test' },
    { id: 'repair', name: 'Repair', icon: Wrench, desc: 'Auto-remediate any test QA issues' },
    { id: 'documentation', name: 'Documentation', icon: BookOpen, desc: 'Synthesize README & API guides' },
    { id: 'validation', name: 'Validation', icon: ShieldCheck, desc: '15-point deployment readiness' },
  ]

  // Determine status of each stage
  const getStageStatus = (stageId, index) => {
    if (!project) return 'pending'
    if (project.status === 'READY') return 'completed'
    if (project.status === 'FAILED' && project.current_stage === stageId) return 'failed'

    const stageOrder = ['requirement', 'planning', 'coding', 'database', 'testing', 'repair', 'documentation', 'validation', 'completed']
    const currentIndex = stageOrder.indexOf(project.current_stage || 'requirement')

    if (index < currentIndex) return 'completed'
    if (index === currentIndex) return 'running'
    return 'pending'
  }

  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollTop = logsEndRef.current.scrollHeight
    }
  }, [logs])

  return (
    <div className="glass-panel" style={{ padding: '1.75rem', marginTop: '1.5rem' }}>
      {/* Pipeline Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Autonomous Agent Pipeline</h3>
            <span className={`badge ${
              project?.status === 'READY' ? 'badge-completed' :
              project?.status === 'FAILED' ? 'badge-failed' :
              project?.status === 'RUNNING' ? 'badge-running' : 'badge-pending'
            }`}>
              {project?.status || 'IDLE'}
            </span>
          </div>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
            Sequential multi-agent execution with automated testing & self-repair.
          </p>
        </div>

        {/* Progress percentage */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '1.5rem', fontWeight: 800, fontFamily: 'var(--font-heading)', color: 'var(--accent-indigo)' }}>
              {project?.progress_pct || 0}%
            </span>
            <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Progress</p>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div style={{ width: '100%', height: '6px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '3px', overflow: 'hidden', marginBottom: '2rem' }}>
        <div style={{
          width: `${project?.progress_pct || 0}%`,
          height: '100%',
          background: project?.status === 'FAILED' ? 'var(--accent-rose)' : 'var(--grad-primary)',
          transition: 'width 0.4s ease-out'
        }}></div>
      </div>

      {/* Agent Stepper Pipeline */}
      <div className="pipeline-track" style={{ marginBottom: '1.75rem' }}>
        {stages.map((stage, idx) => {
          const Icon = stage.icon
          const status = getStageStatus(stage.id, idx)

          return (
            <div key={stage.id} className={`pipeline-node ${status}`}>
              <div className="node-icon-circle">
                {status === 'completed' ? (
                  <CheckCircle2 size={20} />
                ) : status === 'failed' ? (
                  <AlertCircle size={20} />
                ) : (
                  <Icon size={20} />
                )}
              </div>
              <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: status === 'pending' ? 'var(--text-muted)' : 'var(--text-main)' }}>
                {stage.name}
              </h4>
              <span className={`badge badge-${status}`} style={{ marginTop: '0.35rem', fontSize: '0.65rem' }}>
                {status.toUpperCase()}
              </span>
            </div>
          )
        })}
      </div>

      {/* Terminal Live Logs */}
      <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 600 }}>
            <Terminal size={16} color="var(--accent-indigo)" />
            <span>Agent Event Stream ({logs.length} events)</span>
          </div>

          <button
            onClick={() => setShowLogs(!showLogs)}
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.75rem' }}
          >
            <span>{showLogs ? 'Collapse Stream' : 'Expand Stream'}</span>
            {showLogs ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </button>
        </div>

        {showLogs && (
          <div className="terminal-stream" ref={logsEndRef}>
            {logs.length === 0 ? (
              <div style={{ color: 'var(--text-muted)', padding: '1rem', textAlign: 'center' }}>
                Ready. Enter a project description above and click Generate Project to start.
              </div>
            ) : (
              logs.map((log, i) => (
                <div key={i} className="log-line">
                  <span className="log-time">
                    {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : '--:--:--'}
                  </span>
                  <span className={`log-badge log-badge-${log.level || 'INFO'}`}>
                    {log.stage || 'SYS'}
                  </span>
                  <span style={{ flex: 1, wordBreak: 'break-word' }}>
                    {log.message}
                  </span>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  )
}
