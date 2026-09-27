import React, { useState } from 'react';
import OperatorLoginModal from '../components/OperatorLoginModal';
import OperatorDashboard from '../components/OperatorDashboard';

export default function OperatorView({ currentLang }) {
  const [operatorUser, setOperatorUser] = useState(() => {
    const saved = localStorage.getItem('railflow_operator');
    return saved ? JSON.parse(saved) : null;
  });

  const handleLoginSuccess = (userData) => {
    setOperatorUser(userData);
    localStorage.setItem('railflow_operator', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setOperatorUser(null);
    localStorage.removeItem('railflow_operator');
  };

  if (!operatorUser) {
    return <OperatorLoginModal onLoginSuccess={handleLoginSuccess} currentLang={currentLang} />;
  }

  return <OperatorDashboard operatorUser={operatorUser} onLogout={handleLogout} currentLang={currentLang} />;
}
