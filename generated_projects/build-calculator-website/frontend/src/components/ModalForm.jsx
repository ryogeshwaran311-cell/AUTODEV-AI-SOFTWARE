import React, { useState, useEffect } from 'react'
import { X } from 'lucide-react'

export default function ModalForm({ title, initialData, onClose, onSubmit }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    status: 'Active',
    description: '',
    category: 'General',
    ...(initialData || {})
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={e => e.stopPropagation()} style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>{title}</h2>
          <button 
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.4rem', fontWeight: 500 }}>
              Title / Name *
            </label>
            <input 
              type="text" 
              name="name" 
              required
              className="form-input"
              value={formData.name || ''}
              onChange={handleChange}
              placeholder="Enter record name or title"
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.4rem', fontWeight: 500 }}>
              Email / Identifier
            </label>
            <input 
              type="text" 
              name="email" 
              className="form-input"
              value={formData.email || ''}
              onChange={handleChange}
              placeholder="e.g. user@example.com or ID code"
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.4rem', fontWeight: 500 }}>
                Status
              </label>
              <select name="status" className="form-select" value={formData.status || 'Active'} onChange={handleChange}>
                <option value="Active">Active</option>
                <option value="Pending">Pending</option>
                <option value="Completed">Completed</option>
                <option value="Inactive">Inactive</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.4rem', fontWeight: 500 }}>
                Category / Grade
              </label>
              <input 
                type="text" 
                name="category" 
                className="form-input"
                value={formData.category || 'General'}
                onChange={handleChange}
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.4rem', fontWeight: 500 }}>
              Description / Remarks
            </label>
            <textarea 
              name="description" 
              rows={3}
              className="form-textarea"
              value={formData.description || ''}
              onChange={handleChange}
              placeholder="Add optional notes or descriptions..."
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Save Record
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}