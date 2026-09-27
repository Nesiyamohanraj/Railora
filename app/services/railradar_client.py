"""
RailRadar API Integration Client — RailFlow AI

IMPORTANT DISCLAIMER & CONSTRAINT NOTE:
RailRadar (api.railradar.org) is an unofficial third-party API for live train data.
It is NOT an official government feed or CRIS/NTES internal API.
This module isolates all external calls and degrades gracefully to historical dataset replayed state
when RailRadar is unreachable or encounters HTTP/network timeouts.
"""
import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.config import RAILRADAR_BASE_URL

logger = logging.getLogger(__name__)


def fetch_railradar_live_data(train_id: str) -> Dict[str, Any]:
    """
    Attempts to fetch live status for train_id from third-party RailRadar API.
    If unavailable or timed out, gracefully degrades to replayed mock state.
    """
    # RailRadar is an unofficial third-party API
    url = f"{RAILRADAR_BASE_URL}/api/v1/train/{train_id}/live"
    try:
        response = requests.get(url, timeout=2.5)
        if response.status_code == 200:
            data = response.json()
            return {
                "source": "railradar_live_third_party",
                "train_id": str(data.get("train_number", train_id)),
                "train_name": str(data.get("train_name", f"Express {train_id}")),
                "station": str(data.get("current_station_code", "NDLS")),
                "delay_minutes": float(data.get("delay_minutes", 0.0)),
                "speed_kmh": float(data.get("speed_kmh", 55.0)),
                "timestamp": datetime.now().isoformat(),
                "next_station": str(data.get("next_station_code", "CNB")),
                "previous_station": str(data.get("prev_station_code", "ORIGIN")),
                "distance_covered_km": float(data.get("distance_covered_km", 210.0)),
                "total_route_km": float(data.get("total_route_km", 1380.0)),
            }
        else:
            logger.warning(f"RailRadar API returned HTTP {response.status_code}. Falling back to historical replay.")
    except Exception as e:
        logger.info(f"RailRadar API unreachable ({e}). Using historical replay fallback.")

    # Graceful degradation fallback
    return get_fallback_replayed_train_data(train_id)


def get_fallback_replayed_train_data(train_id: str) -> Dict[str, Any]:
    """
    Returns replayed/mock train state when third-party RailRadar is offline.
    """
    known_sample_trains = {
        "12951": {
            "train_id": "12951",
            "train_name": "Mumbai Rajdhani Express",
            "station": "KOTA",
            "delay_minutes": 18.0,
            "speed_kmh": 78.0,
            "next_station": "RTM",
            "previous_station": "SWM",
            "distance_covered_km": 465.0,
            "total_route_km": 1384.0,
        },
        "12002": {
            "train_id": "12002",
            "train_name": "Bhopal Shatabdi Express",
            "station": "AGC",
            "delay_minutes": 5.0,
            "speed_kmh": 90.0,
            "next_station": "GWL",
            "previous_station": "MTH",
            "distance_covered_km": 198.0,
            "total_route_km": 701.0,
        },
        "12424": {
            "train_id": "12424",
            "train_name": "Dibrugarh Rajdhani Express",
            "station": "CNB",
            "delay_minutes": 35.0,
            "speed_kmh": 42.0,
            "next_station": "PRYJ",
            "previous_station": "ALJN",
            "distance_covered_km": 440.0,
            "total_route_km": 2430.0,
        },
    }

    if train_id in known_sample_trains:
        record = known_sample_trains[train_id].copy()
    else:
        record = {
            "train_id": train_id,
            "train_name": f"Superfast Express {train_id}",
            "station": "NDLS",
            "delay_minutes": 12.0,
            "speed_kmh": 60.0,
            "next_station": "CNB",
            "previous_station": "ORIGIN",
            "distance_covered_km": 150.0,
            "total_route_km": 1000.0,
        }

    record["source"] = "historical_replay_fallback"
    record["timestamp"] = datetime.now().isoformat()
    return record
