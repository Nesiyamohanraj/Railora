"""
Congestion Generator Module — RailFlow AI

SYNTHETIC CONGESTION ENGINE:
Since live track section-occupancy data is not publicly exposed by Indian Railways / CRIS feeds,
section congestion is synthetically modeled here.
It is correlated with:
1. Time of day (morning & evening peak hours)
2. Section type (Trunk main lines > Junction bottlenecks > Branch lines)
3. Day type (Festival > Weekend > Weekday)
4. Existing train delay levels in the corridor
Plus controlled variance — not arbitrary random noise.
"""
from datetime import datetime
import math
import random
from typing import Optional


def compute_synthetic_congestion_score(
    section_id: str,
    section_type: str = "trunk",
    timestamp: Optional[datetime] = None,
    day_type: str = "weekday",
    current_delay_min: float = 0.0,
    active_trains_count: int = 3
) -> float:
    """
    Computes a realistic synthetic congestion score between 0.0 (completely free) and 1.0 (gridlock).
    Annotated: Synthetic calculation for SIH 2026 Problem Statement 26028.
    """
    if timestamp is None:
        timestamp = datetime.now()

    hour = timestamp.hour + (timestamp.minute / 60.0)

    # 1. Time-of-Day Factor (Peak hours: 07:30 - 10:30 and 17:00 - 20:30)
    # Dual Gaussian peak modeling
    morning_peak = math.exp(-((hour - 9.0) ** 2) / 3.0)
    evening_peak = math.exp(-((hour - 18.5) ** 2) / 3.5)
    time_factor = max(morning_peak, evening_peak) * 0.35 # Adds up to 0.35

    # 2. Section Type Base Weight
    sec_type_clean = section_type.lower()
    if "trunk" in sec_type_clean:
        base_sec_factor = 0.35
    elif "junction" in sec_type_clean or "jn" in sec_type_clean:
        base_sec_factor = 0.45
    elif "terminal" in sec_type_clean:
        base_sec_factor = 0.50
    else:  # branch
        base_sec_factor = 0.15

    # 3. Day Type Factor
    d_clean = day_type.lower()
    if "festival" in d_clean:
        day_factor = 0.20
    elif "weekend" in d_clean:
        day_factor = 0.10
    else:
        day_factor = 0.0

    # 4. Existing Delay & Active Trains Cascading Pressure
    delay_factor = min(current_delay_min / 120.0, 1.0) * 0.15
    train_density_factor = min(active_trains_count / 10.0, 1.0) * 0.15

    # 5. Seeded controlled noise for deterministic simulation stability
    random.seed(hash(f"{section_id}_{timestamp.hour}") % 100000)
    noise = random.gauss(0.0, 0.03)

    raw_score = base_sec_factor + time_factor + day_factor + delay_factor + train_density_factor + noise

    # Bound strictly between 0.05 and 0.98
    congestion_score = round(max(0.05, min(0.98, raw_score)), 3)
    return congestion_score
