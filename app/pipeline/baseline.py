"""
Baseline NTES Model — RailFlow AI

STATIC NTES-STYLE RULE FORMULA:
Replicates legacy static NTES formula:
  Baseline Projected Delay = Current Delay + (Remaining Distance / Scheduled Speed) * Recovery Buffer
Used strictly for internal benchmarking and operator analytics comparison.
NEVER exposed in passenger-facing API fields.
"""
from typing import Dict, Any
from app.config import DEFAULT_RECOVERY_FACTOR, DEFAULT_AVG_SPEED_KMH


def compute_ntes_baseline_delay(
    current_delay_min: float,
    remaining_distance_km: float = 200.0,
    scheduled_speed_kmh: float = DEFAULT_AVG_SPEED_KMH,
    recovery_factor: float = DEFAULT_RECOVERY_FACTOR
) -> float:
    """
    Computes rule-based static baseline delay prediction.
    Rule logic:
    1. Assumes train runs at constant scheduled speed over remaining distance.
    2. Applies fixed recovery buffer (e.g. 15% slack allowance in schedule).
    """
    if scheduled_speed_kmh <= 0:
        scheduled_speed_kmh = DEFAULT_AVG_SPEED_KMH

    remaining_travel_time_hours = remaining_distance_km / scheduled_speed_kmh
    estimated_recovery_minutes = (remaining_travel_time_hours * 60.0) * recovery_factor

    # Fixed NTES recovery reduces current delay slightly over long distances if positive
    baseline_projected_delay = max(0.0, current_delay_min - estimated_recovery_minutes)
    return round(baseline_projected_delay, 2)
