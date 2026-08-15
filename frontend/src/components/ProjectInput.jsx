import React from 'react'
import { Zap, Rocket, Key, BookOpen, ShoppingBag, Kanban, Stethoscope } from 'lucide-react'

export default function ProjectInput({
  prompt,
  setPrompt,
  onGenerate,
  generating,
  geminiConfig,
  onOpenApiKeyModal
}) {
  const templates = [
    {
      label: "Student Management System",
      icon: BookOpen,
      text: "Build a Student Management System with Admin Login, Student CRUD, Attendance Management, Search, Dashboard and SQLite database."
    },
    {
      label: "E-Commerce Micro-Store",
      icon: ShoppingBag,
      text: "Build an E-Commerce Management System with Product CRUD, Category Filtering, Order Tracking, Customer Analytics and Inventory."
    },
    {
      label: "Team Kanban Board",
      icon: Kanban,
      text: "Build a Project Management and Kanban Board System with Task CRUD, Status Pipelines, Priority Badges, Team assignments and Analytics."
    },
    {
      label: "Clinic & Patient System",
      icon: Stethoscope,
      text: "Build a Clinic Management System with Doctor Profiles, Patient Records CRUD, Appointment Scheduling, Medical History and Dashboard."
    }
  ]

  const handleSubmit = (e, directDeploy = false) => {
    if (e) e.preventDefault()
    if (!prompt.trim() || generating) return
    onGenerate(prompt, directDeploy)
  }

  return (
    <div className="glass-panel-elevated" style={{ padding: '2rem', position: 'relative' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800, background: 'var(--grad-primary)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Autonomous Multi-Agent Engineer
          </h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            Describe your full-stack application. AutoDevAI plans, codes, tests, repairs, and packages everything autonomously.
          </p>
        </div>

        {/* Gemini API Key Status Pill */}
        <button
          onClick={onOpenApiKeyModal}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.4rem 0.85rem',
            borderRadius: 'var(--radius-full)',
            background: geminiConfig?.gemini_configured ? 'rgba(16, 185, 129, 0.15)' : 'rgba(99, 102, 241, 0.15)',
            border: `1px solid ${geminiConfig?.gemini_configured ? 'rgba(16, 185, 129, 0.35)' : 'rgba(99, 102, 241, 0.35)'}`,
            color: geminiConfig?.gemini_configured ? '#34d399' : '#a5b4fc',
            fontSize: '0.75rem',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
        >
          <Key size={14} />
          <span>{geminiConfig?.gemini_configured ? `Gemini Active (${geminiConfig.gemini_model || '2.5-flash'})` : "Configure Gemini Key"}</span>
        </button>
      </div>

      <form onSubmit={(e) => handleSubmit(e, false)}>
        <div style={{ position: 'relative', marginBottom: '1.25rem' }}>
          <textarea
            rows={4}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={generating}
            placeholder="e.g. Build a Student Management System with Admin Login, Student CRUD, Attendance Management, Search and Dashboard..."
            style={{
              width: '100%',
              padding: '1.2rem 1.25rem',
              background: 'rgba(0, 0, 0, 0.4)',
              border: '1px solid var(--border-medium)',
              borderRadius: 'var(--radius-lg)',
              color: '#ffffff',
              fontSize: '1rem',
              lineHeight: '1.6',
              outline: 'none',
              fontFamily: 'var(--font-sans)',
              resize: 'vertical',
              boxShadow: 'inset 0 2px 8px rgba(0, 0, 0, 0.5)'
            }}
          />
        </div>

        {/* Preset Idea Template Chips */}
        <div style={{ marginBottom: '1.5rem' }}>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Instant Idea Presets:
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {templates.map((tpl, i) => {
              const Icon = tpl.icon
              return (
                <button
                  key={i}
                  type="button"
                  disabled={generating}
                  onClick={() => setPrompt(tpl.text)}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    padding: '0.35rem 0.75rem',
                    background: 'rgba(255, 255, 255, 0.04)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-full)',
                    color: 'var(--text-secondary)',
                    fontSize: '0.75rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)'
                    e.currentTarget.style.borderColor = 'var(--border-medium)'
                    e.currentTarget.style.color = '#fff'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)'
                    e.currentTarget.style.borderColor = 'var(--border-subtle)'
                    e.currentTarget.style.color = 'var(--text-secondary)'
                  }}
                >
                  <Icon size={13} color="var(--accent-indigo)" />
                  <span>{tpl.label}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Generate Action Buttons: Normal & Direct Deploy */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <button
            type="button"
            disabled={!prompt.trim() || generating}
            onClick={(e) => handleSubmit(e, true)}
            className="btn btn-cyan btn-lg"
            style={{ fontWeight: 700, padding: '0.85rem 1.5rem' }}
            title="Generate application and automatically open single-service cloud deploy"
          >
            <Rocket size={18} />
            <span>Generate &amp; Direct Deploy</span>
          </button>

          <button
            type="submit"
            disabled={!prompt.trim() || generating}
            className="btn btn-primary btn-lg"
            style={{ fontWeight: 700, padding: '0.85rem 1.75rem', minWidth: '220px' }}
          >
            {generating ? (
              <>
                <span className="spinner" style={{
                  width: '18px',
                  height: '18px',
                  border: '2px solid rgba(255,255,255,0.3)',
                  borderTopColor: '#fff',
                  borderRadius: '50%',
                  display: 'inline-block',
                  animation: 'spinSlow 1s linear infinite'
                }}></span>
                <span>Engineering Application...</span>
              </>
            ) : (
              <>
                <Zap size={18} />
                <span>⚡ GENERATE PROJECT</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
