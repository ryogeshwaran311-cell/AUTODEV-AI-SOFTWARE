import React, { useState } from 'react'
import { X, Key, CheckCircle, Sparkles, Cpu } from 'lucide-react'

export default function ApiKeyModal({ isOpen, onClose, currentConfig, onSaveConfig }) {
  const [apiKey, setApiKey] = useState('')
  const [selectedModel, setSelectedModel] = useState(currentConfig?.gemini_model || 'gemini-2.5-flash')
  const [saving, setSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)

  if (!isOpen) return null

  const handleSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          gemini_api_key: apiKey.trim() || undefined,
          gemini_model: selectedModel
        })
      })
      const data = await res.json()
      if (data.success) {
        setSaveSuccess(true)
        onSaveConfig(data)
        setTimeout(() => {
          setSaveSuccess(false)
          onClose()
        }, 1200)
      }
    } catch (err) {
      console.error('Failed to update Gemini config:', err)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '520px' }}>
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'rgba(99, 102, 241, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-indigo)' }}>
              <Key size={18} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Google Gemini Configuration</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Configure your Gemini API key and active model</p>
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSave} style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
              Gemini API Key
            </label>
            <input 
              type="password"
              className="form-input"
              placeholder={currentConfig?.gemini_configured ? "•••••••••••••••••••••••• (Configured)" : "AIzaSy..."}
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                background: 'rgba(0,0,0,0.3)',
                border: '1px solid var(--border-medium)',
                borderRadius: 'var(--radius-md)',
                color: '#fff',
                fontSize: '0.9rem',
                fontFamily: 'var(--font-mono)'
              }}
            />
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.4rem' }}>
              Get a free API key at <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer" style={{ color: 'var(--accent-indigo)', textDecoration: 'none' }}>Google AI Studio</a>. If omitted, AutoDevAI uses its high-grade offline heuristic generation engine.
            </p>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
              AI Model Selection
            </label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                background: '#0a0e17',
                border: '1px solid var(--border-medium)',
                borderRadius: 'var(--radius-md)',
                color: '#fff',
                fontSize: '0.9rem'
              }}
            >
              <option value="gemini-2.5-flash">Gemini 2.5 Flash (Recommended - Fastest & High Quality)</option>
              <option value="gemini-1.5-flash">Gemini 1.5 Flash (High Throughput)</option>
              <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
              <option value="gemini-1.5-pro">Gemini 1.5 Pro (Deep Architecture)</option>
            </select>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saveSuccess ? (
                <>
                  <CheckCircle size={16} /> Saved!
                </>
              ) : (
                <>
                  <Sparkles size={16} /> Save Configuration
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
