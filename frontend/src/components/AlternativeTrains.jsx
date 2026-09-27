import React, { useState, useEffect } from 'react';
import { ArrowUpRight, ShieldCheck, AlertCircle, GitMerge, Clock, Train } from 'lucide-react';
import { getAlternativeTrainsRoute } from '../services/api';
import { translations } from '../i18n/translations';

export default function AlternativeTrains({ trainNumber = '12951', currentLang }) {
  const [altData, setAltData] = useState(null);
  const t = translations[currentLang] || translations.en;

  useEffect(() => {
    async function loadAlternatives() {
      const data = await getAlternativeTrainsRoute(trainNumber);
      setAltData(data);
    }
    loadAlternatives();
  }, [trainNumber]);

  if (!altData) return null;

  const { delay_minutes, reason_type, blocking_train_id, has_alternative, alternative_type, direct, chained } = altData;

  return (
    <div className="card" style={{
      backgroundColor: has_alternative ? '#fffbeb' : 'rgba(255, 255, 255, 0.9)',
      border: `1px solid ${has_alternative ? '#fde68a' : 'var(--border-color)'}`,
      marginBottom: '24px'
    }}>
      {/* Delay Root Cause Header */}
      <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <h3 style={{ fontSize: '1.15rem', color: has_alternative ? 'var(--warning-amber)' : 'var(--brand-navy)', margin: '0 0 4px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={20} color={has_alternative ? 'var(--warning-amber)' : 'var(--brand-navy)'} />
            Delay Root Cause & Alternative Routes
          </h3>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', margin: 0 }}>
            Root Cause: <strong>{reason_type === 'conflict' ? `Blocked by Train #${blocking_train_id} on section` : 'Operational speed restriction & signal hold'}</strong> (Delay: ~+{delay_minutes}m)
          </p>
        </div>

        {has_alternative && (
          <span className="badge badge-warning">
            <GitMerge size={14} /> Alternative Routes Found ({alternative_type.toUpperCase()})
          </span>
        )}
      </div>

      {/* DIRECT ALTERNATIVE OPTION */}
      {has_alternative && alternative_type === 'direct' && direct && (
        <div style={{
          backgroundColor: '#ffffff',
          borderRadius: 'var(--radius-md)',
          border: '1px solid #fde68a',
          padding: '16px',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--brand-navy)' }}>
              🚆 {direct.train_name}
            </span>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, backgroundColor: 'var(--success-light)', color: 'var(--success-green)', padding: '4px 10px', borderRadius: '99px' }}>
              Direct Express — Arrives {direct.predicted_arrival}
            </span>
          </div>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', margin: 0 }}>
            Departs from same origin. Predicted arrival at destination is <strong>&gt;15 mins earlier</strong> than delayed train.
          </p>
        </div>
      )}

      {/* CHAINED MULTI-LEG ALTERNATIVE OPTION */}
      {has_alternative && alternative_type === 'chained' && chained && (
        <div style={{
          backgroundColor: '#ffffff',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--brand-border)',
          padding: '18px',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <span style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--brand-blue)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            🔗 CHAINED MULTI-LEG ITINERARY (Total Journey: {chained.total_journey_time_minutes} mins)
          </span>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px', marginTop: '12px' }}>
            {/* Leg 1 Card */}
            <div style={{ backgroundColor: 'var(--brand-light)', padding: '12px 14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--brand-border)' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--brand-blue)' }}>LEG 1</span>
              <strong style={{ display: 'block', fontSize: '0.95rem', color: 'var(--text-primary)' }}>Train #{chained.leg_1.train_id}</strong>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', display: 'block' }}>
                {chained.leg_1.from} ({chained.leg_1.departure}) → {chained.leg_1.to} ({chained.leg_1.predicted_arrival})
              </span>
            </div>

            {/* Connection Buffer */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#ecfdf5', padding: '10px', borderRadius: 'var(--radius-sm)', border: '1px solid #a7f3d0', fontSize: '0.8rem', fontWeight: 700, color: 'var(--success-green)' }}>
              ⏱️ 20+ min Guaranteed Connection Buffer at {chained.leg_1.to}
            </div>

            {/* Leg 2 Card */}
            <div style={{ backgroundColor: 'var(--brand-light)', padding: '12px 14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--brand-border)' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--brand-blue)' }}>LEG 2</span>
              <strong style={{ display: 'block', fontSize: '0.95rem', color: 'var(--text-primary)' }}>Train #{chained.leg_2.train_id}</strong>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', display: 'block' }}>
                {chained.leg_2.from} ({chained.leg_2.departure}) → {chained.leg_2.to} ({chained.leg_2.predicted_arrival})
              </span>
            </div>
          </div>
        </div>
      )}

      {/* NO ALTERNATIVE QUALIFIED */}
      {!has_alternative && (
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', margin: 0 }}>
          No direct or multi-leg alternative train arrives faster for this route window. Proceeding on current train remains optimal.
        </p>
      )}
    </div>
  );
}
