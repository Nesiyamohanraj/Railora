import React from 'react';
import { Bell, X } from 'lucide-react';

export default function DelayAlertBanner({ message, onClose }) {
  if (!message) return null;

  return (
    <div style={{
      backgroundColor: 'var(--brand-navy)',
      color: '#ffffff',
      padding: '12px 20px',
      borderRadius: 'var(--radius-md)',
      marginBottom: '20px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      boxShadow: 'var(--shadow-md)',
      animation: 'fadeIn 0.3s ease-out'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <Bell size={20} color="#bfdbfe" className="pulse-subtle" />
        <span style={{ fontSize: '0.95rem', fontWeight: 600 }}>
          {message}
        </span>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#94a3b8',
            cursor: 'pointer',
            padding: '4px'
          }}
        >
          <X size={18} />
        </button>
      )}
    </div>
  );
}
