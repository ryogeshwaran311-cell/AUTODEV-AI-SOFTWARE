import React from 'react'
import { Edit3, Trash2 } from 'lucide-react'

export default function DataTable({ items = [], onEdit, onDelete, loading }) {
  if (loading) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        Loading records from database...
      </div>
    )
  }

  if (!items || items.length === 0) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        No records found. Click "+ Add" to create your first record.
      </div>
    )
  }

  // Derive dynamic table headers from keys (excluding internal ids / hashes)
  const sample = items[0]
  const keys = Object.keys(sample).filter(k => !k.includes('password') && k !== 'id')

  return (
    <div className="table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            <th>ID</th>
            {keys.map(k => (
              <th key={k}>{k.replace(/_/g, ' ')}</th>
            ))}
            <th style={{ textAlign: 'right' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td style={{ fontWeight: 600, color: 'var(--accent-primary)', fontFamily: 'var(--font-mono)' }}>#{item.id}</td>
              {keys.map(k => (
                <td key={k}>
                  {typeof item[k] === 'boolean' ? (
                    <span className={`badge ${item[k] ? 'badge-success' : 'badge-danger'}`}>
                      {item[k] ? 'Yes' : 'No'}
                    </span>
                  ) : (
                    String(item[k] ?? '-')
                  )}
                </td>
              ))}
              <td style={{ textAlign: 'right' }}>
                <div style={{ display: 'inline-flex', gap: '0.5rem' }}>
                  <button 
                    className="btn btn-secondary btn-sm"
                    onClick={() => onEdit(item)}
                    title="Edit Record"
                  >
                    <Edit3 size={13} />
                  </button>
                  <button 
                    className="btn btn-danger btn-sm"
                    onClick={() => onDelete(item.id)}
                    title="Delete Record"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}