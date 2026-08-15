import React, { useState, useEffect } from 'react'
import { FileCode, Folder, Copy, Check, FileText } from 'lucide-react'

export default function CodeExplorer({ project }) {
  const [files, setFiles] = useState([])
  const [selectedFile, setSelectedFile] = useState('')
  const [fileContent, setFileContent] = useState('')
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)

  // Fetch file list
  useEffect(() => {
    if (!project?.id) return
    fetch(`/api/projects/${project.id}`)
      .then(res => res.json())
      .then(data => {
        if (data.success && data.project?.files) {
          setFiles(data.project.files)
          if (data.project.files.length > 0) {
            const defaultFile = data.project.files.find(f => f.includes('App.jsx')) || data.project.files[0]
            setSelectedFile(defaultFile)
          }
        }
      })
      .catch(console.error)
  }, [project?.id])

  // Fetch selected file content
  useEffect(() => {
    if (!project?.id || !selectedFile) return
    setLoading(true)
    fetch(`/api/projects/${project.id}/files/${selectedFile}`)
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setFileContent(data.content)
        } else {
          setFileContent(`// Error loading file: ${data.error}`)
        }
      })
      .catch(err => setFileContent(`// Network error: ${err.message}`))
      .finally(() => setLoading(false))
  }, [project?.id, selectedFile])

  const handleCopy = () => {
    navigator.clipboard.writeText(fileContent)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="glass-panel" style={{ marginTop: '1.5rem', display: 'flex', height: '650px', overflow: 'hidden' }}>
      {/* File Tree Sidebar */}
      <div style={{
        width: '260px',
        borderRight: '1px solid var(--border-subtle)',
        background: 'rgba(0, 0, 0, 0.4)',
        display: 'flex',
        flexDirection: 'column',
        flexShrink: 0
      }}>
        <div style={{ padding: '1rem', borderBottom: '1px solid var(--border-subtle)', fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-secondary)' }}>
          Workspace Explorer ({files.length} files)
        </div>
        <div style={{ flex: 1, overflowY: 'auto', padding: '0.5rem' }}>
          {files.map((file) => {
            const isSelected = selectedFile === file
            return (
              <button
                key={file}
                onClick={() => setSelectedFile(file)}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.5rem 0.75rem',
                  borderRadius: 'var(--radius-sm)',
                  border: 'none',
                  background: isSelected ? 'rgba(99, 102, 241, 0.2)' : 'transparent',
                  color: isSelected ? '#fff' : 'var(--text-secondary)',
                  fontSize: '0.8rem',
                  fontFamily: 'var(--font-mono)',
                  cursor: 'pointer',
                  textAlign: 'left',
                  textOverflow: 'ellipsis',
                  overflow: 'hidden',
                  whiteSpace: 'nowrap'
                }}
              >
                <FileCode size={14} color={isSelected ? 'var(--accent-indigo)' : 'var(--text-muted)'} />
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>{file}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Code Viewer Panel */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: '#05070d' }}>
        <div style={{
          padding: '0.75rem 1.25rem',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'rgba(0, 0, 0, 0.2)'
        }}>
          <span style={{ fontSize: '0.85rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
            {selectedFile || 'Select a file to inspect'}
          </span>
          <button className="btn btn-secondary btn-sm" onClick={handleCopy} disabled={!fileContent}>
            {copied ? <Check size={13} color="var(--accent-emerald)" /> : <Copy size={13} />}
            <span>{copied ? 'Copied!' : 'Copy Code'}</span>
          </button>
        </div>

        <div style={{ flex: 1, overflow: 'auto', padding: '1.25rem' }}>
          {loading ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Loading source code...</p>
          ) : (
            <pre style={{ margin: 0, fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: '#e2e8f0', lineHeight: 1.6 }}>
              <code>{fileContent}</code>
            </pre>
          )}
        </div>
      </div>
    </div>
  )
}
