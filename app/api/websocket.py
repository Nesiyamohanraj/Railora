"""
WebSocket Real-Time Push Alerts — RailFlow AI
Manages WebSocket connections and broadcasts real-time delay updates & section congestion alerts.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast_alert(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message: {e}")


manager = ConnectionManager()


@router.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint: /ws/alerts
    Pushes real-time alerts and section status updates to clients.
    """
    await manager.connect(websocket)
    try:
        # Send initial connection status message
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "message": "Connected to RailFlow AI Real-Time Alert Engine",
            "active_monitored_corridors": ["NDLS-CNB", "KOTA-RTM", "HWH-ASN"]
        })

        while True:
            # Receive client ping or keep-alive message
            data = await websocket.receive_text()
            # Echo back live health pulse
            await websocket.send_json({
                "type": "PULSE",
                "timestamp": asyncio.get_event_loop().time(),
                "received": data
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket error: {e}")
        manager.disconnect(websocket)
