import React from 'react';
import { Star } from 'lucide-react';
import { translations } from '../i18n/translations';

export default function ReliabilityBadge({ score = 92.4, currentLang }) {
  const t = translations[currentLang] || translations.en;
  const starVal = (score / 20.0).toFixed(1);

  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '6px',
      backgroundColor: '#fef3c7',
      color: '#92400e',
      border: '1px solid #fde68a',
      borderRadius: 'var(--radius-full)',
      padding: '6px 14px',
      fontSize: '0.875rem',
      fontWeight: 700
    }}>
      <Star size={16} fill="#d97706" color="#d97706" />
      <span>{starVal} / 5</span>
      <span style={{ fontWeight: 500, color: '#b45309', fontSize: '0.8rem' }}>({score}% {t.punctualityRating})</span>
    </div>
  );
}
