import React from 'react';
import { GitCommit, ArrowRight, AlertCircle } from 'lucide-react';
import { translations } from '../i18n/translations';

export default function DelayPropagationView({ trainNumber, currentLang }) {
  const t = translations[currentLang] || translations.en;

  // Simple passenger-friendly cascade flow data
  const cascadeFlow = [
    {
      trainId: trainNumber || "12951",
      trainName: "Your Train (Target)",
      status: "Primary Delay Source",
      impact: "Initial 18 min delay",
      isPrimary: true
    },
    {
      trainId: "12002",
      trainName: "Bhopal Shatabdi Express",
      status: "Trailing in same section",
      impact: "+10 min cascade delay caused",
      isPrimary: false
    },
    {
      trainId: "12424",
      trainName: "Dibrugarh Rajdhani",
      status: "Section sequence hold",
      impact: "+6 min cascade delay caused",
      isPrimary: false
    }
  ];

  return (
    <div className="card" style={{ marginBottom: '24px' }}>
      <h3 style={{ fontSize: '1.15rem', color: 'var(--brand-navy)', margin: '0 0 4px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <GitCommit size={20} color="var(--brand-blue)" /> {t.delayCascadeHeader}
      </h3>
      <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '18px' }}>
        {t.cascadeSubtext}
      </p>

      {/* Visual Flow Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px', alignItems: 'center' }}>
        {cascadeFlow.map((item, idx) => (
          <React.Fragment key={item.trainId}>
            <div style={{
              backgroundColor: item.isPrimary ? 'var(--brand-light)' : '#f8fafc',
              border: `1px solid ${item.isPrimary ? 'var(--brand-border)' : 'var(--border-color)'}`,
              borderRadius: 'var(--radius-md)',
              padding: '16px',
              position: 'relative'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: item.isPrimary ? 'var(--brand-blue)' : 'var(--text-muted)' }}>
                  #{item.trainId}
                </span>
                <span className={item.isPrimary ? "badge badge-warning" : "badge badge-info"} style={{ fontSize: '0.75rem', padding: '2px 8px' }}>
                  {item.isPrimary ? 'Target' : 'Affected'}
                </span>
              </div>
              <h4 style={{ fontSize: '0.98rem', color: 'var(--text-primary)', margin: '0 0 4px 0' }}>
                {item.trainName}
              </h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--danger-red)', fontWeight: 600, margin: 0, display: 'flex', alignItems: 'center', gap: '4px' }}>
                <AlertCircle size={14} /> {item.impact}
              </p>
            </div>
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
