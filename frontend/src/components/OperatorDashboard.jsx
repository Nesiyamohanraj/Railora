import React, { useState, useEffect } from 'react';
import { Activity, AlertOctagon, Sliders, Play, LogOut, CheckCircle2 } from 'lucide-react';
import { getNetworkHealth, simulateWhatIf } from '../services/api';
import { translations } from '../i18n/translations';

export default function OperatorDashboard({ operatorUser, onLogout, currentLang }) {
  const [networkState, setNetworkState] = useState(null);
  const [whatIfTrain, setWhatIfTrain] = useState('12951');
  const [whatIfDelay, setWhatIfDelay] = useState(15);
  const [whatIfResult, setWhatIfResult] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);

  const t = translations[currentLang] || translations.en;

  useEffect(() => {
    async function loadData() {
      const data = await getNetworkHealth();
      setNetworkState(data);
    }
    loadData();
  }, []);

  const handleRunSimulation = async () => {
    setIsSimulating(true);
    const res = await simulateWhatIf(whatIfTrain, whatIfDelay);
    setWhatIfResult(res);
    setIsSimulating(false);
  };

  return (
    <div style={{ paddingBottom: '60px' }}>
      {/* Operator Top Bar */}
      <div style={{
        backgroundColor: '#ffffff',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-md)',
        padding: '16px 24px',
        marginBottom: '24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        boxShadow: 'var(--shadow-sm)'
      }}>
        <div>
          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--brand-blue)', textTransform: 'uppercase' }}>
            OPERATOR SESSION ACTIVE
          </span>
          <h2 style={{ fontSize: '1.25rem', color: 'var(--brand-navy)', margin: 0 }}>
            Control Officer: {operatorUser?.id || 'OP-782'} ({operatorUser?.role || 'Senior Controller'})
          </h2>
        </div>
        <button
          className="btn btn-secondary"
          onClick={onLogout}
          style={{ height: '40px', fontSize: '0.875rem' }}
        >
          <LogOut size={16} /> Sign Out
        </button>
      </div>

      {/* Network Health Cards Grid */}
      <h3 style={{ fontSize: '1.2rem', color: 'var(--brand-navy)', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Activity size={20} color="var(--brand-blue)" /> {t.networkHealthHeader}
      </h3>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '28px' }}>
        <div className="card" style={{ padding: '20px' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>{t.activeTrains}</span>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--brand-navy)', marginTop: '4px' }}>
            {networkState?.total_active_trains || 142}
          </div>
          <span style={{ fontSize: '0.78rem', color: 'var(--success-green)', fontWeight: 600 }}>Monitored Across Corridors</span>
        </div>

        <div className="card" style={{ padding: '20px' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>{t.punctualityRate}</span>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--success-green)', marginTop: '4px' }}>
            {networkState?.network_punctuality_rate_pct || 84.5}%
          </div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Target Threshold: 80%</span>
        </div>

        <div className="card" style={{ padding: '20px' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>{t.avgDelay}</span>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--warning-amber)', marginTop: '4px' }}>
            {networkState?.average_delay_minutes || 14.2}m
          </div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Network-wide average</span>
        </div>

        <div className="card" style={{ padding: '20px' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 600 }}>Congestion Index</span>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--brand-blue)', marginTop: '4px' }}>
            {networkState?.overall_congestion_index || 0.48}
          </div>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Scale 0.0 (Clear) to 1.0 (Gridlock)</span>
        </div>
      </div>

      {/* Corridor Bottleneck Alerts */}
      <div className="card" style={{ marginBottom: '28px' }}>
        <h4 style={{ fontSize: '1.05rem', color: 'var(--danger-red)', margin: '0 0 12px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertOctagon size={18} color="var(--danger-red)" /> High-Risk Corridor Bottlenecks
        </h4>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {(networkState?.high_risk_corridors || [
            "Delhi - Kanpur Trunk Corridor",
            "Howrah - Asansol Industrial Belt",
            "Mumbai - Kalyan Junction Throat"
          ]).map((corridor) => (
            <span key={corridor} className="badge badge-warning" style={{ padding: '8px 14px' }}>
              ⚠️ {corridor}
            </span>
          ))}
        </div>
      </div>

      {/* Interactive What-If Simulator */}
      <div className="card" style={{ border: '2px solid var(--brand-border)', backgroundColor: '#ffffff' }}>
        <h3 style={{ fontSize: '1.25rem', color: 'var(--brand-navy)', margin: '0 0 6px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sliders size={20} color="var(--brand-blue)" /> {t.whatIfTitle}
        </h3>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '20px' }}>
          {t.whatIfDescription}
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '20px', marginBottom: '20px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px' }}>
              {t.targetTrain}
            </label>
            <select
              value={whatIfTrain}
              onChange={(e) => setWhatIfTrain(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-color)',
                fontSize: '1rem',
                fontFamily: 'inherit'
              }}
            >
              <option value="12951">12951 — Mumbai Rajdhani</option>
              <option value="12002">12002 — Bhopal Shatabdi</option>
              <option value="12424">12424 — Dibrugarh Rajdhani</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px' }}>
              {t.addedDelayLabel}: <strong>+{whatIfDelay} mins</strong>
            </label>
            <input
              type="range"
              min="5"
              max="60"
              step="5"
              value={whatIfDelay}
              onChange={(e) => setWhatIfDelay(e.target.value)}
              style={{ width: '100%', accentColor: 'var(--brand-blue)', height: '8px' }}
            />
          </div>
        </div>

        <button
          className="btn btn-primary"
          onClick={handleRunSimulation}
          disabled={isSimulating}
          style={{ width: '100%', backgroundColor: 'var(--brand-navy)' }}
        >
          <Play size={18} /> {isSimulating ? 'Simulating Cascade Graph...' : t.simulateBtn}
        </button>

        {/* Simulation Output Breakdown */}
        {whatIfResult && (
          <div className="animate-fade-in" style={{
            marginTop: '24px',
            backgroundColor: 'var(--brand-light)',
            borderRadius: 'var(--radius-md)',
            padding: '20px',
            border: '1px solid var(--brand-border)'
          }}>
            <h4 style={{ fontSize: '1.05rem', color: 'var(--brand-navy)', margin: '0 0 10px 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <CheckCircle2 size={18} color="var(--success-green)" /> Simulation Results
            </h4>

            <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginBottom: '16px' }}>
              <div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{t.affectedTrainsCount}:</span>
                <span style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--danger-red)', display: 'block' }}>
                  {whatIfResult.total_downstream_trains_affected} trains
                </span>
              </div>
              <div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{t.totalNetDelay}:</span>
                <span style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--warning-amber)', display: 'block' }}>
                  +{whatIfResult.network_delay_increase_min} total minutes
                </span>
              </div>
            </div>

            {/* Affected Trains Cards */}
            <div style={{ display: 'grid', gap: '10px' }}>
              {whatIfResult.affected_trains.map((tItem) => (
                <div key={tItem.train_id} style={{ backgroundColor: '#ffffff', padding: '12px 16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <strong style={{ fontSize: '0.95rem', color: 'var(--text-primary)' }}>{tItem.train_name} (#{tItem.train_id})</strong>
                    <span style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)' }}>{tItem.dependency_reason}</span>
                  </div>
                  <span className="badge badge-warning">
                    +{tItem.additional_cascade_delay_min}m cascade
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
