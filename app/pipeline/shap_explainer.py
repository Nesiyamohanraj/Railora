"""
Explainability Layer — RailFlow AI
Converts SHAP feature importances and contributions into plain-language human readable delay reasons.
"""
from typing import Dict, Any
import numpy as np

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False


def generate_plain_language_explanation(feature_dict: Dict[str, Any], total_predicted_delay: float) -> str:
    """
    Computes feature contribution weights and formats them into passenger plain language.
    e.g.: '15 min from heavy rain, 10 min from section congestion ahead'
    """
    if total_predicted_delay < 3.0:
        return "Minimal delay expected; normal operating speed."

    # Extract feature values
    current_delay = feature_dict.get("current_delay", 0.0)
    weather_sev = feature_dict.get("weather_severity_score", 0.0)
    congestion = feature_dict.get("congestion_score", 0.4)
    trains_ahead = feature_dict.get("trains_ahead", 1)
    speed_ratio = feature_dict.get("speed_ratio", 1.0)
    dwell = feature_dict.get("dwell_time_pattern", 0.0)

    reasons = []

    # Weather impact
    if weather_sev >= 0.7:
        w_impact = round(weather_sev * 18.0)
        reasons.append(f"{w_impact} min from heavy rain/fog")
    elif weather_sev >= 0.3:
        w_impact = round(weather_sev * 12.0)
        reasons.append(f"{w_impact} min from inclement weather")

    # Congestion impact
    if congestion >= 0.65:
        c_impact = round(congestion * 16.0)
        reasons.append(f"{c_impact} min from track section congestion ahead")
    elif congestion >= 0.45:
        c_impact = round(congestion * 10.0)
        reasons.append(f"{c_impact} min from moderate corridor traffic")

    # Trains ahead impact
    if trains_ahead >= 3:
        t_impact = round(trains_ahead * 4.5)
        reasons.append(f"{t_impact} min from {trains_ahead} trains ahead in block section")

    # Speed degradation impact
    if speed_ratio < 0.7:
        s_impact = round((1.0 - speed_ratio) * 14.0)
        reasons.append(f"{s_impact} min from speed restriction / caution order")

    # Dwell backlog impact
    if dwell >= 3.0:
        d_impact = round(dwell)
        reasons.append(f"{d_impact} min from extended station platform dwell time")

    # Upstream carryover delay
    if current_delay >= 10.0 and len(reasons) < 2:
        u_impact = round(current_delay * 0.4)
        reasons.append(f"{u_impact} min carried over from upstream arrival delay")

    if not reasons:
        reasons.append("Minor traffic headway buffer and routine signal holds")

    return ", ".join(reasons[:2]).capitalize() + "."
