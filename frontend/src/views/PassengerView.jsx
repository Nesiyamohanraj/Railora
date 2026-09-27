import React, { useState, useEffect } from 'react';
import SearchBox from '../components/SearchBox';
import ETAResultCard from '../components/ETAResultCard';
import PlainDelayReason from '../components/PlainDelayReason';
import LiveMapTrack from '../components/LiveMapTrack';
import DelayPropagationView from '../components/DelayPropagationView';
import AlternativeTrains from '../components/AlternativeTrains';
import DelayAlertBanner from '../components/DelayAlertBanner';
import { predictTrainETA } from '../services/api';
import { translations } from '../i18n/translations';

export default function PassengerView({ currentLang }) {
  const [trainData, setTrainData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [alertMsg, setAlertMsg] = useState('');
  const t = translations[currentLang] || translations.en;

  // Initial load default train (12951) for instant demonstration
  useEffect(() => {
    handleSearch('12951');
  }, []);

  const handleSearch = async (trainId) => {
    setIsLoading(true);
    const result = await predictTrainETA(trainId);
    setTrainData(result);
    setIsLoading(false);

    // Set simple notification banner if late
    if (result.current_status && result.current_status.toLowerCase().includes('late')) {
      setAlertMsg(`Alert: Train ${trainId} is currently running ${result.current_status}. ${result.confidence_trend}`);
    } else {
      setAlertMsg('');
    }
  };

  return (
    <div style={{ paddingBottom: '60px' }}>
      {/* 5-Second Simplicity Search Box */}
      <SearchBox currentLang={currentLang} onSearch={handleSearch} isLoading={isLoading} />

      {/* Delay Trend Notification Banner */}
      {alertMsg && <DelayAlertBanner message={alertMsg} onClose={() => setAlertMsg('')} />}

      {/* Main Results Container */}
      {trainData && (
        <>
          {/* Prominent ETA Range Card */}
          <ETAResultCard data={trainData} currentLang={currentLang} />

          {/* Plain Human Sentence Delay Explanation */}
          <PlainDelayReason reason={trainData.delay_reason} currentLang={currentLang} />

          {/* Route Map & Visual Live Tracker */}
          <LiveMapTrack
            currentPosition={trainData.current_position}
            nextStation={trainData.next_station}
            previousStation={trainData.previous_station}
            currentLang={currentLang}
          />

          {/* Visual Delay Cascade Graph */}
          <DelayPropagationView trainNumber={trainData.train_number} currentLang={currentLang} />

          {/* Quietly Surfaced Alternative Trains (Surfaced when delay > 20 mins) */}
          <AlternativeTrains alternatives={trainData.alternative_trains} currentLang={currentLang} />
        </>
      )}
    </div>
  );
}
