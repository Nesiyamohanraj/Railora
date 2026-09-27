"""
Weather API Integration Client — RailFlow AI
Provides live and historical weather tags for station locations.
Degrades gracefully to 'clear' weather if API is unavailable.
"""
import requests
import logging
from typing import Dict, Any

from app.config import OPENWEATHER_API_KEY

logger = logging.getLogger(__name__)


def fetch_weather_for_station(station_code: str, lat: float = 28.6139, lon: float = 77.2090) -> str:
    """
    Fetches weather condition tag for station.
    Returns string: 'clear', 'light_rain', 'heavy_rain', 'fog', etc.
    """
    if OPENWEATHER_API_KEY == "demo_key":
        # Heuristic fallback based on station zone/code
        if station_code in ["DDB", "GHY", "NJP"]:
            return "heavy_rain"
        elif station_code in ["NDLS", "CNB", "PRYJ"]:
            return "fog"
        else:
            return "clear"

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
    try:
        resp = requests.get(url, timeout=2.0)
        if resp.status_code == 200:
            data = resp.json()
            main_w = data.get("weather", [{}])[0].get("main", "").lower()
            if "rain" in main_w:
                return "heavy_rain" if "heavy" in main_w else "light_rain"
            elif "fog" in main_w or "mist" in main_w or "haze" in main_w:
                return "fog"
            else:
                return "clear"
    except Exception as e:
        logger.warning(f"Weather API request failed: {e}")

    return "clear"
