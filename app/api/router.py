"""
Central Router Assembly — RailFlow AI
Combines REST endpoints and WebSocket router.
"""
from fastapi import APIRouter
from app.api.endpoints import router as rest_router
from app.api.websocket import router as ws_router

api_router = APIRouter()
api_router.include_router(rest_router)
api_router.include_router(ws_router)
