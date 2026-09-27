import React from 'react';
import { ShieldAlert, Globe, UserCheck, Train } from 'lucide-react';
import { translations } from '../i18n/translations';

export default function Header({ currentLang, onLangChange, activeMode, onModeChange, isOperatorLoggedIn }) {
  const t = translations[currentLang] || translations.en;

  return (
    <header style={{
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      backdropFilter: 'blur(10px)',
      borderBottom: '1px solid var(--border-color)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      boxShadow: 'var(--shadow-sm)'
    }}>
      <div className="container" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '76px'
      }}>
        {/* Logo Image and Brand Title */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', cursor: 'pointer' }} onClick={() => onModeChange('passenger')}>
          <img
            src="/logo.jpg"
            alt="RailFlow AI Logo"
            onError={(e) => { e.target.style.display = 'none'; }}
            style={{
              height: '48px',
              width: '48px',
              objectFit: 'cover',
              borderRadius: 'var(--radius-md)',
              border: '2px solid var(--brand-border)',
              boxShadow: 'var(--shadow-sm)'
            }}
          />
          <div>
            <h1 style={{ fontSize: '1.4rem', color: 'var(--brand-navy)', margin: 0, lineHeight: 1.2, fontWeight: 800 }}>
              {t.appTitle}
            </h1>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0, fontWeight: 500 }}>
              {t.subTitle}
            </p>
          </div>
        </div>

        {/* Right Section: Language Selector & Mode Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          {/* Language Selector Dropdown */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', backgroundColor: 'var(--bg-subtle)', padding: '6px 12px', borderRadius: 'var(--radius-full)' }}>
            <Globe size={16} color="var(--text-secondary)" />
            <select
              value={currentLang}
              onChange={(e) => onLangChange(e.target.value)}
              style={{
                background: 'transparent',
                border: 'none',
                fontFamily: 'inherit',
                fontWeight: 600,
                fontSize: '0.875rem',
                color: 'var(--text-primary)',
                cursor: 'pointer',
                outline: 'none'
              }}
            >
              <option value="en">English</option>
              <option value="hi">हिंदी (Hindi)</option>
              <option value="mr">मराठी (Marathi)</option>
              <option value="ta">தமிழ் (Tamil)</option>
            </select>
          </div>

          {/* Mode Switcher Buttons */}
          <div style={{ display: 'flex', gap: '6px', backgroundColor: 'var(--bg-subtle)', padding: '4px', borderRadius: 'var(--radius-md)' }}>
            <button
              className="btn"
              onClick={() => onModeChange('passenger')}
              style={{
                height: '38px',
                padding: '0 14px',
                fontSize: '0.875rem',
                backgroundColor: activeMode === 'passenger' ? '#ffffff' : 'transparent',
                color: activeMode === 'passenger' ? 'var(--brand-navy)' : 'var(--text-secondary)',
                boxShadow: activeMode === 'passenger' ? 'var(--shadow-sm)' : 'none',
                border: 'none'
              }}
            >
              <Train size={16} />
              {t.passengerTab}
            </button>
            <button
              className="btn"
              onClick={() => onModeChange('operator')}
              style={{
                height: '38px',
                padding: '0 14px',
                fontSize: '0.875rem',
                backgroundColor: activeMode === 'operator' ? 'var(--brand-navy)' : 'transparent',
                color: activeMode === 'operator' ? '#ffffff' : 'var(--text-secondary)',
                boxShadow: activeMode === 'operator' ? 'var(--shadow-sm)' : 'none',
                border: 'none'
              }}
            >
              {isOperatorLoggedIn ? <UserCheck size={16} /> : <ShieldAlert size={16} />}
              {t.operatorTab}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
