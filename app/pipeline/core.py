"""
Master Unified Core Pipeline — RailFlow AI

UNIFIED ENTRY POINT:
Every endpoint (/predict, /train/{id}/live, /propagation, /whatif) calls this core pipeline function.
Pipeline sequence:
1. Ingestion & Normalization
2. Synthetic Congestion Engine
3. Feature Engineering
4. Baseline (NTES Static Formula) Calculation
5. Core ML (XGBoost) Model Prediction
6. NetworkX Graph Delay Cascade Simulation
7. Quantile Uncertainty Bounds
8. SHAP Plain-Language Explanation
9. Formatted Passenger & Operator Payload Construction
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

from app.pipeline.ingestion import normalize_record, load_raw_datasets
from app.pipeline.congestion import compute_synthetic_congestion_score
from app.pipeline.features import extract_features
from app.pipeline.baseline import compute_ntes_baseline_delay
from app.pipeline.model import predict_additional_delay
from app.pipeline.graph import build_propagation_graph, simulate_cascade
from app.pipeline.uncertainty import compute_uncertainty_bands
from app.pipeline.shap_explainer import generate_plain_language_explanation
from app.models.response import (
    PassengerPredictResponse,
    ETARange,
    CurrentPosition,
    AlternativeTrain,
)

logger = logging.getLogger(__name__)


def run_railflow_pipeline(
    train_id: str,
    current_station: str = "NDLS",
    current_delay_min: float = 0.0,
    departure_timestamp: Optional[str] = None,
    hypothetical_added_delay: float = 0.0,
    live_raw_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Master unified pipeline function called by all endpoints.
    Returns dictionary containing normalized raw data, baseline delay, ML delay,
    network cascade effects, uncertainty ranges, and passenger formatted response.
    """
    # 1. Ingestion & Normalization
    raw_payload = live_raw_data or {
        "train_id": train_id,
        "station": current_station,
        "delay_minutes": current_delay_min,
        "timestamp": departure_timestamp or datetime.now().isoformat(),
    }
    norm_data = normalize_record(raw_payload)

    # 2. Congestion score
    sec_id = norm_data["section_id"]
    sec_type = norm_data["section_type"]
    day_type = norm_data["day_type"]

    # 3. Feature extraction
    feature_dict = extract_features(norm_data, trains_in_section=2)

    # 4. Baseline NTES rule model (Internal benchmarking only, not in passenger view)
    baseline_delay = compute_ntes_baseline_delay(
        current_delay_min=norm_data["delay_minutes"],
        remaining_distance_km=norm_data["total_route_km"] - norm_data["distance_covered_km"]
    )

    # 5. Core ML model (XGBoost)
    ml_additional_delay = predict_additional_delay(feature_dict)

    # Combine current delay + hypothetical delay + ML additional delay
    total_predicted_delay = max(0.0, norm_data["delay_minutes"] + hypothetical_added_delay + ml_additional_delay)

    # 6. NetworkX Graph Cascade Simulation
    simulated_trains = [
        norm_data,
        {
            "train_id": "12002",
            "train_name": "Shatabdi Express",
            "station": current_station,
            "section_id": sec_id,
            "delay_minutes": 5.0,
            "distance_covered_km": norm_data["distance_covered_km"] - 15.0
        },
        {
            "train_id": "12424",
            "train_name": "Rajdhani Express",
            "station": current_station,
            "section_id": sec_id,
            "delay_minutes": 12.0,
            "distance_covered_km": norm_data["distance_covered_km"] - 35.0
        }
    ]
    G = build_propagation_graph(simulated_trains)
    cascade_impacts = simulate_cascade(G, train_id, ml_additional_delay + hypothetical_added_delay)

    # 7. Uncertainty Layer (Quantile bounds)
    uncertainty_dict, confidence_trend = compute_uncertainty_bands(
        predicted_delay_50th=total_predicted_delay,
        distance_covered_km=norm_data["distance_covered_km"],
        total_route_km=norm_data["total_route_km"],
        weather_severity=feature_dict["weather_severity_score"],
        congestion_score=feature_dict["congestion_score"]
    )

    # 8. Explainability Layer (SHAP)
    plain_delay_reason = generate_plain_language_explanation(feature_dict, total_predicted_delay)

    # Format ETA timestamps
    now = datetime.now()
    min_eta_dt = now + timedelta(minutes=uncertainty_dict["min_delay_min"] + 30)
    max_eta_dt = now + timedelta(minutes=uncertainty_dict["max_delay_min"] + 30)

    eta_range = ETARange(
        min_eta=min_eta_dt.strftime("%H:%M"),
        max_eta=max_eta_dt.strftime("%H:%M"),
        min_delay_min=uncertainty_dict["min_delay_min"],
        max_delay_min=uncertainty_dict["max_delay_min"],
        expected_delay_min=uncertainty_dict["expected_delay_min"]
    )

    # Status string
    if total_predicted_delay <= 5.0:
        status_str = "On Time"
    else:
        status_str = f"{int(total_predicted_delay)} min late"

    # Alternative trains (populated only if delay > 20 mins)
    alternatives = []
    if total_predicted_delay >= 20.0:
        alternatives = [
            AlternativeTrain(
                train_number="12004",
                train_name="Lucknow Shatabdi",
                departure_time=(now + timedelta(minutes=45)).strftime("%H:%M"),
                arrival_time=(now + timedelta(hours=6, minutes=15)).strftime("%H:%M"),
                historical_reliability_score=94.2,
                expected_delay_min=4.0
            ),
            AlternativeTrain(
                train_number="22436",
                train_name="Vande Bharat Express",
                departure_time=(now + timedelta(minutes=90)).strftime("%H:%M"),
                arrival_time=(now + timedelta(hours=8)).strftime("%H:%M"),
                historical_reliability_score=97.8,
                expected_delay_min=0.0
            )
        ]

    # Construction of Passenger Response Schema
    passenger_response = PassengerPredictResponse(
        train_name=norm_data["train_name"],
        train_number=norm_data["train_id"],
        predicted_eta_range=eta_range,
        current_status=status_str,
        delay_reason=plain_delay_reason,
        current_position=CurrentPosition(
            station_code=norm_data["station"],
            station_name=f"Station {norm_data['station']}",
            latitude=28.6139,
            longitude=77.2090
        ),
        next_station=norm_data["next_station"],
        previous_station=norm_data["previous_station"],
        historical_reliability_score=88.5,
        confidence_trend=confidence_trend,
        alternative_trains=alternatives
    )

    return {
        "passenger_response": passenger_response,
        "norm_data": norm_data,
        "feature_dict": feature_dict,
        "baseline_delay": baseline_delay,
        "ml_additional_delay": ml_additional_delay,
        "total_predicted_delay": total_predicted_delay,
        "cascade_impacts": cascade_impacts,
        "graph": G,
    }
