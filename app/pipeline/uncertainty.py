"""
Uncertainty Layer — RailFlow AI
Computes quantile uncertainty bands (10th, 50th, 90th percentiles) for predicted train delays.
Generates narrowing confidence trend as the train nears its destination.
"""
from typing import Dict, Any, Tuple


def compute_uncertainty_bands(
    predicted_delay_50th: float,
    distance_covered_km: float = 150.0,
    total_route_km: float = 1380.0,
    weather_severity: float = 0.0,
    congestion_score: float = 0.4
) -> Tuple[Dict[str, Any], str]:
    """
    Computes 10th, 50th, and 90th percentile delay bounds.
    The variance / band width contracts as progress fraction -> 1.0 (narrowing indicator).
    """
    total_route_km = max(total_route_km, 1.0)
    progress_ratio = min(max(distance_covered_km / total_route_km, 0.0), 1.0)
    remaining_fraction = 1.0 - progress_ratio

    # Base variance spread in minutes (larger spread far from destination)
    base_spread = (15.0 * remaining_fraction) + (weather_severity * 8.0) + (congestion_score * 10.0)

    # 10th percentile (best case / lower bound)
    min_delay = round(max(0.0, predicted_delay_50th - (base_spread * 0.65)), 1)

    # 50th percentile (median expected)
    exp_delay = round(max(0.0, predicted_delay_50th), 1)

    # 90th percentile (worst case / upper bound)
    max_delay = round(max(exp_delay, predicted_delay_50th + (base_spread * 0.85)), 1)

    # Confidence trend narrowing indicator
    if progress_ratio >= 0.75:
        confidence_trend = "Narrowing (High Confidence — Approaching Destination)"
    elif progress_ratio >= 0.40:
        confidence_trend = "Moderate Spread (Mid-Journey)"
    else:
        confidence_trend = "Wide Spread (Early Journey — Subject to En-Route Delays)"

    uncertainty_dict = {
        "min_delay_min": min_delay,
        "expected_delay_min": exp_delay,
        "max_delay_min": max_delay,
    }

    return uncertainty_dict, confidence_trend
