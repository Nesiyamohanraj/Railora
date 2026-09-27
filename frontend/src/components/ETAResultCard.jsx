import React from 'react';
import { Clock, ShieldCheck, AlertTriangle, ArrowRight, MapPin } from 'lucide-react';
import { translations } from '../i18n/translations';
import ReliabilityBadge from './ReliabilityBadge';

export default function ETAResultCard({ data, currentLang }) {
  if (!data) return null;

  const t = translations[currentLang] || translations.en;
  const eta = data.predicted_eta_range || {};
  const isLate = data.current_status && !data.current_status.toLowerCase().includes('on time');

  return (
    <div className="card animate-fade-in" style={{
      borderLeft: `6px solid ${isLate ? 'var(--warning-amber)' : 'var(--success-green)'}`,
      marginBottom: '24px'
    }}>
      {/* Train Title & Status Row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px', marginBottom: '20px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h2 style={{ fontSize: '1.6rem', color: 'var(--brand-navy)', margin: 0 }}>
              {data.train_name}
            </h2>
            <span style={{
              backgroundColor: 'var(--bg-subtle)',
              color: 'var(--text-secondary)',
              fontWeight: 700,
              fontSize: '0.9rem',
              padding: '4px 10px',
              borderRadius: 'var(--radius-sm)'
            }}>
              #{data.train_number}
            </span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <MapPin size={16} color="var(--brand-blue)" />
            Current Station: <strong>{data.current_position?.station_name || data.current_position?.station_code}</strong>
            <ArrowRight size={14} color="var(--text-muted)" />
            Next: <strong>{data.next_station}</strong>
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* Status Badge */}
          <span className={isLate ? "badge badge-warning" : "badge badge-success"} style={{ fontSize: '0.95rem', padding: '8px 16px' }}>
            {isLate ? <AlertTriangle size={18} /> : <ShieldCheck size={18} />}
            {data.current_status}
          </span>
          {/* Historical Reliability Badge */}
          <ReliabilityBadge score={data.historical_reliability_score} currentLang={currentLang} />
        </div>
      </div>

      {/* Prominent ETA Range Box */}
      <div style={{
        backgroundColor: isLate ? 'var(--warning-light)' : 'var(--brand-light)',
        border: `1px solid ${isLate ? '#fde68a' : 'var(--brand-border)'}`,
        borderRadius: 'var(--radius-md)',
        padding: '24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '20px'
      }}>
        <div>
          <span style={{
            fontSize: '0.875rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            color: isLate ? 'var(--warning-amber)' : 'var(--brand-blue)',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            <Clock size={16} /> {t.expectedArrival}
          </span>
          {/* Unmissable ETA Range Text */}
          <div style={{
            fontSize: '2.5rem',
            fontWeight: 800,
            fontFamily: 'var(--font-heading)',
            color: 'var(--text-primary)',
            lineHeight: 1.1,
            marginTop: '6px'
          }}>
            {eta.min_eta} – {eta.max_eta} PM
          </div>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '6px' }}>
            Expected delay band: <strong>+{eta.min_delay_min} to +{eta.max_delay_min} mins</strong> (Median: ~+{eta.expected_delay_min}m)
          </p>
        </div>

        {/* Confidence Label */}
        <div style={{
          backgroundColor: '#ffffff',
          padding: '14px 20px',
          borderRadius: 'var(--radius-md)',
          boxShadow: 'var(--shadow-sm)',
          border: '1px solid var(--border-color)',
          maxWidth: '300px'
        }}>
          <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', display: 'block' }}>
            {t.confidenceLabel}
          </span>
          <span style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--success-green)', display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px' }}>
            <ShieldCheck size={18} color="var(--success-green)" />
            {data.confidence_trend || t.highConfidence}
          </span>
        </div>
      </div>
    </div>
  );
}
