"""
Main FastAPI Application Entry Point — Railora
Problem Statement 26028 (Dynamic Forecast of ETA for Coaching Trains)
Smart India Hackathon 2026
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.router import api_router
from app.services.logger_service import init_feedback_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("railora")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Railora Backend...")
    init_feedback_db()
    logger.info("Railora Backend initialized successfully.")
    yield
    logger.info("Shutting down Railora Backend...")


app = FastAPI(
    title="Railora — Backend API",
    description=(
        "Dynamic train ETA prediction system modeling delays as network propagation problems. "
        "Built for Smart India Hackathon 2026 (Problem Statement 26028)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Enable CORS for HTML/CSS/JS and React frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include main API router
app.include_router(api_router)


@app.get("/", summary="Root System Status")
def root_status():
    return {
        "system": "Railora — Dynamic Train ETA Prediction Backend",
        "status": "Online",
        "version": "1.0.0",
        "documentation": "/docs",
        "disclaimer": "Live train status powered by third-party RailRadar API. Track section congestion is synthetically modeled."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
