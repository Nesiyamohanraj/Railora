import React, { useState } from 'react';
import { Lock, User, ShieldCheck, KeyRound } from 'lucide-react';
import { translations } from '../i18n/translations';

export default function OperatorLoginModal({ onLoginSuccess, currentLang }) {
  const [operatorId, setOperatorId] = useState('OP-782');
  const [password, setPassword] = useState('railflow123');
  const [errorMsg, setErrorMsg] = useState('');
  const t = translations[currentLang] || translations.en;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (operatorId.trim() && password.trim()) {
      // Basic authenticated session
      onLoginSuccess({
        id: operatorId.trim(),
        role: 'Senior Network Controller',
        token: 'token_op_' + Date.now()
      });
    } else {
      setErrorMsg('Please enter both Operator ID and Password.');
    }
  };

  return (
    <div style={{
      maxWidth: '420px',
      margin: '60px auto',
      backgroundColor: '#ffffff',
      borderRadius: 'var(--radius-lg)',
      border: '1px solid var(--border-color)',
      boxShadow: 'var(--shadow-lg)',
      padding: '36px',
      textAlign: 'center'
    }}>
      <div style={{
        width: '56px',
        height: '56px',
        backgroundColor: 'var(--brand-light)',
        color: 'var(--brand-navy)',
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        margin: '0 auto 16px auto',
        border: '1px solid var(--brand-border)'
      }}>
        <KeyRound size={28} color="var(--brand-navy)" />
      </div>

      <h2 style={{ fontSize: '1.4rem', color: 'var(--brand-navy)', margin: '0 0 6px 0' }}>
        {t.operatorLoginTitle}
      </h2>
      <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '24px' }}>
        Authenticated portal for railway control room officers & network dispatchers.
      </p>

      {errorMsg && (
        <div style={{
          backgroundColor: 'var(--danger-light)',
          color: 'var(--danger-red)',
          padding: '10px',
          borderRadius: 'var(--radius-sm)',
          fontSize: '0.85rem',
          marginBottom: '16px'
        }}>
          {errorMsg}
        </div>
      )}

      {/* Minimal 2-field form */}
      <form onSubmit={handleSubmit} style={{ textAlign: 'left' }}>
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px' }}>
            {t.operatorIdLabel}
          </label>
          <div style={{ display: 'flex', alignItems: 'center', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', padding: '0 12px', backgroundColor: '#ffffff' }}>
            <User size={18} color="var(--text-muted)" style={{ marginRight: '8px' }} />
            <input
              type="text"
              value={operatorId}
              onChange={(e) => setOperatorId(e.target.value)}
              placeholder="e.g. OP-782"
              required
              style={{
                width: '100%',
                border: 'none',
                outline: 'none',
                padding: '12px 0',
                fontSize: '0.95rem',
                fontFamily: 'inherit'
              }}
            />
          </div>
        </div>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px' }}>
            {t.passwordLabel}
          </label>
          <div style={{ display: 'flex', alignItems: 'center', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', padding: '0 12px', backgroundColor: '#ffffff' }}>
            <Lock size={18} color="var(--text-muted)" style={{ marginRight: '8px' }} />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              style={{
                width: '100%',
                border: 'none',
                outline: 'none',
                padding: '12px 0',
                fontSize: '0.95rem',
                fontFamily: 'inherit'
              }}
            />
          </div>
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          style={{ width: '100%', backgroundColor: 'var(--brand-navy)' }}
        >
          <ShieldCheck size={18} /> {t.loginBtn}
        </button>
      </form>

      <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '20px' }}>
        Demo Credentials pre-filled for evaluation. Click Sign In to open Dashboard.
      </p>
    </div>
  );
}
