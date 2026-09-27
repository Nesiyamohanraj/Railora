import React from 'react';
import { Train, Radio, CheckCircle, MapPin, Gauge } from 'lucide-react';
import { translations } from '../i18n/translations';

export default function LiveMapTrack({ currentPosition, nextStation, previousStation, currentLang }) {
  const t = translations[currentLang] || translations.en;

  const rawStnCode = currentPosition?.station_code || 'AGC';
  let rawStnName = currentPosition?.station_name || 'Agra Cantt';

  // Format station name if it has redundant "Station " prefix
  if (rawStnName.startsWith('Station ')) {
    rawStnName = rawStnName.replace('Station ', '') + ' Junction';
  }

  const prevStn = previousStation && previousStation !== 'ORIGIN' ? previousStation : 'Mathura Jn (MTJ)';
  const nextStn = nextStation && nextStation !== 'DESTINATION' ? nextStation : 'Gwalior Jn (GWL)';

  return (
    <div className="card" style={{
      marginBottom: '24px',
      background: 'linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)',
      border: '1px solid var(--border-color)',
      boxShadow: 'var(--shadow-md)'
    }}>
      {/* Top Header & Status Badges */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '22px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h3 style={{ fontSize: '1.2rem', color: 'var(--brand-navy)', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Train size={22} color="var(--brand-blue)" /> {t.routeProgress}
          </h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: '2px 0 0 0' }}>
            Real-time track section position & upcoming station progress
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {/* Live Speed Badge */}
          <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            backgroundColor: '#f1f5f9',
            color: 'var(--text-primary)',
            fontSize: '0.82rem',
            fontWeight: 700,
            padding: '4px 10px',
            borderRadius: 'var(--radius-full)',
            border: '1px solid var(--border-color)'
          }}>
            <Gauge size={14} color="var(--brand-blue)" /> 78 km/h
          </span>

          {/* Tracking Badge */}
          <span className="badge badge-info" style={{ fontSize: '0.82rem', padding: '6px 14px' }}>
            <Radio size={14} className="pulse-subtle" color="var(--brand-blue)" /> {t.liveTrackingBadge}
          </span>
        </div>
      </div>

      {/* Premium Transit Timeline Line */}
      <div style={{
        position: 'relative',
        padding: '36px 24px',
        backgroundColor: '#ffffff',
        borderRadius: 'var(--radius-md)',
        border: '1px solid #cbd5e1',
        boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.02)'
      }}>
        {/* Background Track Line */}
        <div style={{
          position: 'absolute',
          top: '52px',
          left: '70px',
          right: '70px',
          height: '6px',
          backgroundColor: '#e2e8f0',
          borderRadius: '3px',
          zIndex: 1
        }}>
          {/* Progress Filled Segment */}
          <div style={{
            width: '48%',
            height: '100%',
            background: 'linear-gradient(90deg, #2563eb 0%, #1e3a8a 100%)',
            borderRadius: '3px'
          }} />
        </div>

        {/* Stations Node Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1.4fr 1fr 1fr',
          position: 'relative',
          zIndex: 2,
          alignItems: 'flex-start'
        }}>
          {/* 1. Passed Station (Origin / Previous) */}
          <div style={{ textAlign: 'center' }}>
            <div style={{
              width: '26px',
              height: '26px',
              borderRadius: '50%',
              backgroundColor: '#ecfdf5',
              border: '2px solid var(--success-green)',
              color: 'var(--success-green)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 10px auto'
            }}>
              <CheckCircle size={14} />
            </div>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              PASSED STOP
            </span>
            <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '2px' }}>
              {prevStn}
            </div>
          </div>

          {/* 2. Active Current Location Node (Highlighted Hero) */}
          <div style={{ textAlign: 'center' }}>
            <div style={{
              width: '46px',
              height: '46px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%)',
              color: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '-10px auto 8px auto',
              boxShadow: '0 0 0 6px rgba(37, 99, 235, 0.2), 0 4px 12px rgba(30, 58, 138, 0.35)',
              position: 'relative'
            }}>
              <Train size={22} />
            </div>
            <span style={{
              fontSize: '0.72rem',
              fontWeight: 800,
              backgroundColor: 'var(--brand-light)',
              color: 'var(--brand-blue)',
              padding: '2px 8px',
              borderRadius: '99px',
              letterSpacing: '0.05em',
              border: '1px solid var(--brand-border)'
            }}>
              LIVE LOCATION
            </span>
            <div style={{ fontSize: '1.08rem', fontWeight: 800, color: 'var(--brand-navy)', marginTop: '4px' }}>
              {rawStnName} ({rawStnCode})
            </div>
          </div>

          {/* 3. Next Stop */}
          <div style={{ textAlign: 'center' }}>
            <div style={{
              width: '26px',
              height: '26px',
              borderRadius: '50%',
              backgroundColor: '#ffffff',
              border: '2px solid #94a3b8',
              margin: '0 auto 10px auto'
            }} />
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--brand-blue)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              NEXT STOP
            </span>
            <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '2px' }}>
              {nextStn}
            </div>
          </div>

          {/* 4. Final Destination */}
          <div style={{ textAlign: 'center' }}>
            <div style={{
              width: '26px',
              height: '26px',
              borderRadius: '50%',
              backgroundColor: '#ffffff',
              border: '2px dashed #cbd5e1',
              margin: '0 auto 10px auto'
            }} />
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              TERMINUS
            </span>
            <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '2px' }}>
              Bhopal Jn (BPL)
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
