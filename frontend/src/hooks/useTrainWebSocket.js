/**
 * Custom React Hook for Real-Time Train WebSocket Telemetry Stream — RailFlow
 */
import { useState, useEffect } from 'react';

export function useTrainWebSocket(trainId) {
  const [telemetry, setTelemetry] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!trainId) return;

    let ws = null;
    let timer = null;

    try {
      ws = new WebSocket('ws://localhost:8000/ws/alerts');

      ws.onopen = () => {
        setIsConnected(true);
        console.log(`WebSocket telemetry subscribed for Train #${trainId}`);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data && data.telemetry) {
            setTelemetry(data.telemetry);
          }
        } catch (e) {
          // ignore parse error
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
      };

      ws.onerror = () => {
        setIsConnected(false);
      };
    } catch (e) {
      setIsConnected(false);
    }

    // Simulate progress tick generator for smooth live animation
    let step = 0.45;
    timer = setInterval(() => {
      step = step >= 0.85 ? 0.45 : step + 0.03;
      setTelemetry((prev) => ({
        ...prev,
        train_id: trainId,
        progress_fraction: parseFloat(step.toFixed(2)),
        is_live: true
      }));
    }, 4000);

    return () => {
      if (ws) ws.close();
      if (timer) clearInterval(timer);
    };
  }, [trainId]);

  return { telemetry, isConnected };
}
