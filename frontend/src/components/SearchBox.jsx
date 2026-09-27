import React, { useState } from 'react';
import { Search, Sparkles } from 'lucide-react';
import { translations } from '../i18n/translations';

export default function SearchBox({ currentLang, onSearch, isLoading }) {
  const [inputVal, setInputVal] = useState('');
  const t = translations[currentLang] || translations.en;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputVal.trim()) {
      onSearch(inputVal.trim());
    }
  };

  const handleQuickSelect = (trainNum) => {
    setInputVal(trainNum);
    onSearch(trainNum);
  };

  return (
    <div style={{ margin: '28px 0' }}>
      <form onSubmit={handleSubmit} style={{ position: 'relative', width: '100%' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          backgroundColor: '#ffffff',
          borderRadius: 'var(--radius-lg)',
          border: '2px solid var(--brand-border)',
          boxShadow: 'var(--shadow-md)',
          padding: '6px 8px 6px 20px',
          transition: 'border-color 0.15s ease'
        }}>
          <Search size={24} color="var(--text-muted)" style={{ flexShrink: 0, marginRight: '12px' }} />
          <input
            type="text"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder={t.searchPlaceholder}
            style={{
              width: '100%',
              border: 'none',
              outline: 'none',
              fontSize: '1.15rem',
              fontFamily: 'inherit',
              color: 'var(--text-primary)',
              padding: '12px 0'
            }}
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={isLoading}
            style={{
              padding: '0 28px',
              fontSize: '1rem',
              borderRadius: 'var(--radius-md)',
              flexShrink: 0
            }}
          >
            {isLoading ? 'Searching...' : t.searchBtn}
          </button>
        </div>
      </form>

      {/* Quick Demo Search Pills for Instant 5-second testing */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '16px', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Sparkles size={14} color="var(--brand-blue)" /> {t.popularTrains}
        </span>
        <button
          className="badge badge-info"
          onClick={() => handleQuickSelect('12951')}
          style={{ cursor: 'pointer', border: '1px solid var(--brand-border)' }}
        >
          12951 — Mumbai Rajdhani
        </button>
        <button
          className="badge badge-info"
          onClick={() => handleQuickSelect('12002')}
          style={{ cursor: 'pointer', border: '1px solid var(--brand-border)' }}
        >
          12002 — Bhopal Shatabdi
        </button>
        <button
          className="badge badge-info"
          onClick={() => handleQuickSelect('12424')}
          style={{ cursor: 'pointer', border: '1px solid var(--brand-border)' }}
        >
          12424 — Dibrugarh Rajdhani
        </button>
      </div>
    </div>
  );
}
