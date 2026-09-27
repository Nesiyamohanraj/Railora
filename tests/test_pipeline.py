"""
Unit Tests — RailFlow AI Pipeline Modules
Tests ingestion normalization, congestion generator, feature extraction,
baseline calculation, XGBoost prediction, NetworkX cascade, and uncertainty estimation.
"""
import pytest
from datetime import datetime

from app.pipeline.ingestion import normalize_record, join_historical_weather
from app.pipeline.congestion import compute_synthetic_congestion_score
from app.pipeline.features import extract_features, features_to_matrix
from app.pipeline.baseline import compute_ntes_baseline_delay
from app.pipeline.model import predict_additional_delay
from app.pipeline.graph import build_propagation_graph, simulate_cascade
from app.pipeline.uncertainty import compute_uncertainty_bands
from app.pipeline.shap_explainer import generate_plain_language_explanation
from app.pipeline.core import run_railflow_pipeline


def test_ingestion_normalization():
    raw = {
        "train_id": "12951",
        "station": "KOTA",
        "delay_minutes": 25.0,
        "timestamp": "2026-09-20T10:00:00"
    }
    norm = normalize_record(raw)
    assert norm["train_id"] == "12951"
    assert norm["station"] == "KOTA"
    assert norm["delay_minutes"] == 25.0
    assert "weather_tag" in norm
    assert "section_id" in norm


def test_congestion_generator():
    score_peak = compute_synthetic_congestion_score("SEC_NDLS_CNB", "trunk", datetime(2026, 9, 20, 9, 0))
    score_night = compute_synthetic_congestion_score("SEC_NDLS_CNB", "trunk", datetime(2026, 9, 20, 3, 0))
    assert 0.0 <= score_peak <= 1.0
    assert 0.0 <= score_night <= 1.0
    assert score_peak > score_night, "Peak hour congestion should be higher than off-peak night hours"


def test_feature_extraction():
    norm = {
        "train_id": "12951",
        "delay_minutes": 15.0,
        "speed_kmh": 45.0,
        "weather_tag": "heavy_rain",
        "section_id": "SEC_NDLS_CNB",
        "section_type": "trunk",
        "day_type": "weekday"
    }
    feats = extract_features(norm, trains_in_section=3)
    assert feats["current_delay"] == 15.0
    assert feats["weather_severity_score"] >= 0.7
    mat = features_to_matrix(feats)
    assert mat.shape == (1, 8)


def test_baseline_vs_ml_separation():
    baseline = compute_ntes_baseline_delay(current_delay_min=30.0, remaining_distance_km=400.0)
    feats = {
        "current_delay": 30.0,
        "speed_ratio": 0.8,
        "trains_ahead": 2,
        "weather_severity_score": 0.3,
        "congestion_score": 0.5,
        "day_type_code": 0,
        "dwell_time_pattern": 2.0,
        "historical_section_delay_rate": 10.0
    }
    ml_delay = predict_additional_delay(feats)
    assert isinstance(baseline, float)
    assert isinstance(ml_delay, float)
    assert ml_delay >= 0.0


def test_networkx_propagation_cascade():
    trains = [
        {"train_id": "12951", "train_name": "Train A", "section_id": "SEC_1", "delay_minutes": 30.0, "distance_covered_km": 200.0},
        {"train_id": "12002", "train_name": "Train B", "section_id": "SEC_1", "delay_minutes": 5.0, "distance_covered_km": 180.0},
    ]
    G = build_propagation_graph(trains)
    assert G.number_of_nodes() == 3 # 2 trains + 1 section
    cascade = simulate_cascade(G, "12951", additional_delay_min=15.0)
    assert len(cascade) == 1
    assert cascade[0]["train_id"] == "12002"
    assert cascade[0]["additional_cascade_delay_min"] > 0.0


def test_uncertainty_quantiles():
    bands, trend = compute_uncertainty_bands(predicted_delay_50th=20.0, distance_covered_km=1100.0, total_route_km=1380.0)
    assert bands["min_delay_min"] <= bands["expected_delay_min"] <= bands["max_delay_min"]
    assert "Narrowing" in trend


def test_shap_plain_language_explainer():
    feats = {
        "current_delay": 20.0,
        "weather_severity_score": 0.8,
        "congestion_score": 0.7,
        "trains_ahead": 4,
        "speed_ratio": 0.6,
        "dwell_time_pattern": 1.0
    }
    reason = generate_plain_language_explanation(feats, total_predicted_delay=35.0)
    assert isinstance(reason, str)
    assert len(reason) > 5


def test_unified_core_pipeline():
    res = run_railflow_pipeline("12951", "NDLS", current_delay_min=15.0)
    assert "passenger_response" in res
    assert res["passenger_response"].train_number == "12951"
    assert res["passenger_response"].current_status is not None
    assert res["passenger_response"].delay_reason is not None
