/**
 * WebSocket Real-Time Alert Manager — RailFlow AI
 * Listens for live delay alerts from /ws/alerts with graceful reconnection logic.
 */

export class AlertWebSocketManager {
  constructor(onMessageCallback) {
    this.url = 'ws://localhost:8000/ws/alerts';
    this.onMessageCallback = onMessageCallback;
    this.ws = null;
    this.reconnectTimer = null;
  }

  connect() {
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('Connected to RailFlow AI Real-Time WebSocket Alerts');
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (this.onMessageCallback) {
            this.onMessageCallback(data);
          }
        } catch (e) {
          console.warn('Error parsing WebSocket message:', e);
        }
      };

      this.ws.onclose = () => {
        // Try auto-reconnecting after 10 seconds
        this.reconnectTimer = setTimeout(() => this.connect(), 10000);
      };

      this.ws.onerror = (err) => {
        console.warn('WebSocket connection error:', err);
      };
    } catch (e) {
      console.warn('WebSocket unavailable:', e);
    }
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.ws) this.ws.close();
  }
}
