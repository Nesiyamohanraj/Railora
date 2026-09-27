import React, { useState } from 'react';
import Header from './components/Header';
import PassengerView from './views/PassengerView';
import OperatorView from './views/OperatorView';

export default function App() {
  const [currentLang, setCurrentLang] = useState('en');
  const [activeMode, setActiveMode] = useState('passenger'); // 'passenger' | 'operator'
  const [isOperatorLoggedIn, setIsOperatorLoggedIn] = useState(() => {
    return !!localStorage.getItem('railflow_operator');
  });

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Universal Header */}
      <Header
        currentLang={currentLang}
        onLangChange={setCurrentLang}
        activeMode={activeMode}
        onModeChange={setActiveMode}
        isOperatorLoggedIn={isOperatorLoggedIn}
      />

      {/* Main Screen Content */}
      <main className="container" style={{ flex: 1, paddingTop: '20px' }}>
        {activeMode === 'passenger' ? (
          <PassengerView currentLang={currentLang} />
        ) : (
          <OperatorView currentLang={currentLang} />
        )}
      </main>

      {/* Footer */}
      <footer style={{
        backgroundColor: 'rgba(255, 255, 255, 0.92)',
        backdropFilter: 'blur(10px)',
        borderTop: '1px solid var(--border-color)',
        padding: '24px 0',
        textAlign: 'center',
        color: 'var(--text-muted)',
        fontSize: '0.85rem'
      }}>
        <div className="container">
          <p style={{ margin: '0 0 4px 0', fontWeight: 600, color: 'var(--brand-navy)' }}>
            Railora — Dynamic Train Forecast & Delay Cascade Engine
          </p>
          <p style={{ margin: 0 }}>
            Smart India Hackathon 2026 • Problem Statement 26028 • Designed for Simplicity & Accessibility
          </p>
        </div>
      </footer>
    </div>
  );
}
