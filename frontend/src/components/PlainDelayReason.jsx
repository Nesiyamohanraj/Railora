import React from 'react';
import { Info } from 'lucide-react';
import { translations } from '../i18n/translations';

export default function PlainDelayReason({ reason, currentLang }) {
  if (!reason) return null;

  const t = translations[currentLang] || translations.en;

  return (
    <div className="card" style={{
      backgroundColor: '#f8fafc',
      border: '1px solid #cbd5e1',
      marginBottom: '24px',
      padding: '18px 24px',
      display: 'flex',
      alignItems: 'center',
      gap: '14px'
    }}>
      <div style={{
        backgroundColor: '#e2e8f0',
        color: 'var(--brand-navy)',
        padding: '10px',
        borderRadius: 'var(--radius-full)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0
      }}>
        <Info size={20} color="var(--brand-navy)" />
      </div>
      <div>
        <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.04em' }}>
          {t.delayReasonHeader}
        </span>
        <p style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-primary)', margin: '2px 0 0 0' }}>
          "{reason}"
        </p>
      </div>
    </div>
  );
}
