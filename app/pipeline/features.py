"""
Feature Engineering Module — RailFlow AI
Transforms raw normalized train observation into standard ML feature vector.
"""
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from app.pipeline.congestion import compute_synthetic_congestion_score


WEATHER_SEVERITY_MAP = {
    "clear": 0.0,
    "sunny": 0.0,
    "cloudy": 0.1,
    "light_rain": 0.3,
    "heavy_rain": 0.7,
    "fog": 0.8,
    "dense_fog": 0.95,
    "storm": 0.90,
}

DAY_TYPE_MAP = {
    "weekday": 0,
    "weekend": 1,
    "festival": 2,
}

FEATURE_COLUMNS = [
    "current_delay",
    "speed_ratio",
    "trains_ahead",
    "weather_severity_score",
    "congestion_score",
    "day_type_code",
    "dwell_time_pattern",
    "historical_section_delay_rate",
]


def extract_features(normalized_data: Dict[str, Any], trains_in_section: int = 2) -> Dict[str, Any]:
    """
    Computes feature vector for XGBoost/LightGBM model inference.
    """
    current_delay = float(normalized_data.get("delay_minutes", 0.0))

    # Speed ratio (actual current speed / historical scheduled average speed)
    current_speed = float(normalized_data.get("speed_kmh") or 50.0)
    hist_avg_speed = float(normalized_data.get("hist_avg_speed") or 60.0)
    speed_ratio = round(min(max(current_speed / max(hist_avg_speed, 1.0), 0.1), 2.0), 3)

    # Trains ahead in section
    trains_ahead = int(trains_in_section)

    # Weather severity
    weather_tag = str(normalized_data.get("weather_tag", "clear")).lower()
    weather_severity_score = WEATHER_SEVERITY_MAP.get(weather_tag, 0.2)

    # Congestion score
    section_id = str(normalized_data.get("section_id", "SEC_MAIN"))
    section_type = str(normalized_data.get("section_type", "trunk"))
    day_type = str(normalized_data.get("day_type", "weekday"))
    congestion_score = compute_synthetic_congestion_score(
        section_id=section_id,
        section_type=section_type,
        day_type=day_type,
        current_delay_min=current_delay,
        active_trains_count=trains_ahead + 1,
    )

    # Day type code
    day_type_code = DAY_TYPE_MAP.get(day_type.lower(), 0)

    # Dwell time pattern (extra dwell time at stations in minutes)
    sched_dwell = float(normalized_data.get("scheduled_dwell_min") or 2.0)
    act_dwell = float(normalized_data.get("actual_dwell_min") or 4.0)
    dwell_time_pattern = round(act_dwell - sched_dwell, 2)

    # Historical section delay rate (mins delayed per 100km on this section)
    hist_delay_rate = float(normalized_data.get("hist_section_delay_rate") or 12.5)

    feature_dict = {
        "current_delay": current_delay,
        "speed_ratio": speed_ratio,
        "trains_ahead": trains_ahead,
        "weather_severity_score": weather_severity_score,
        "congestion_score": congestion_score,
        "day_type_code": day_type_code,
        "dwell_time_pattern": dwell_time_pattern,
        "historical_section_delay_rate": hist_delay_rate,
    }

    return feature_dict


def features_to_matrix(feature_dict: Dict[str, Any]) -> np.ndarray:
    """Converts feature dict to 2D numpy array in proper column order."""
    row = [feature_dict[col] for col in FEATURE_COLUMNS]
    return np.array([row], dtype=np.float32)
