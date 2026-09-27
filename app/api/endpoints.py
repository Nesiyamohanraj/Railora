"""
REST API Endpoints — RailFlow AI
Implements all required REST API routes.
Each endpoint delegates execution to the core pipeline functions.
"""
from fastapi import APIRouter, HTTPException, Query, Path as APIPath
from typing import List, Dict, Any
from datetime import datetime

from app.models.request import PredictRequest, WhatIfRequest
from app.models.response import (
    PassengerPredictResponse,
    PropagationResponse,
    WhatIfResponse,
    NetworkHealthResponse,
    CascadedTrainDetail,
    SectionCongestionOverview,
)
from app.pipeline.core import run_railflow_pipeline
from app.pipeline.alternatives import evaluate_train_alternatives
from app.services.railradar_client import fetch_railradar_live_data, get_fallback_replayed_train_data
from app.services.logger_service import log_prediction_event

router = APIRouter()


@router.post("/predict", response_model=PassengerPredictResponse, summary="Predict Train ETA (Passenger Facing)")
def predict_eta(request: PredictRequest):
    try:
        pipeline_result = run_railflow_pipeline(
            train_id=request.train_id,
            current_station=request.current_station,
            current_delay_min=request.current_delay_minutes or 0.0,
            departure_timestamp=request.departure_timestamp
        )

        log_prediction_event(
            train_id=request.train_id,
            station_code=request.current_station,
            baseline_delay_min=pipeline_result["baseline_delay"],
            ml_predicted_delay_min=pipeline_result["ml_additional_delay"],
            total_predicted_delay_min=pipeline_result["total_predicted_delay"],
            weather_tag=pipeline_result["norm_data"]["weather_tag"],
            congestion_score=pipeline_result["feature_dict"]["congestion_score"],
            delay_reason=pipeline_result["passenger_response"].delay_reason
        )

        return pipeline_result["passenger_response"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error processing prediction: {str(e)}")


@router.get("/sample_trains", summary="Get Demo / Sample Train Data")
def get_sample_trains():
    samples = [
        get_fallback_replayed_train_data("12951"),
        get_fallback_replayed_train_data("12002"),
        get_fallback_replayed_train_data("12424"),
    ]
    return {
        "status": "success",
        "sample_count": len(samples),
        "data": samples
    }


@router.get("/train/{id}/live", response_model=PassengerPredictResponse, summary="Fetch Live RailRadar Data + Predict")
def get_live_train_prediction(
    id: str = APIPath(..., description="Train number / ID e.g. 12951")
):
    try:
        live_data = fetch_railradar_live_data(id)
        pipeline_result = run_railflow_pipeline(
            train_id=id,
            current_station=live_data["station"],
            current_delay_min=live_data["delay_minutes"],
            live_raw_data=live_data
        )
        return pipeline_result["passenger_response"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Live train prediction error: {str(e)}")


@router.get("/propagation/{section_id}", response_model=PropagationResponse, summary="Get Section Delay Cascade Effect")
def get_section_propagation(
    section_id: str = APIPath(..., description="Track section ID e.g. SEC_NDLS_CNB")
):
    try:
        pipeline_result = run_railflow_pipeline(
            train_id="12951",
            current_station="NDLS",
            current_delay_min=25.0
        )

        cascaded_details = [
            CascadedTrainDetail(**item) for item in pipeline_result["cascade_impacts"]
        ]

        graph_summary = {
            "total_nodes": pipeline_result["graph"].number_of_nodes(),
            "total_edges": pipeline_result["graph"].number_of_edges(),
            "section_id": section_id,
            "corridor_type": "Trunk Main Line",
            "bottleneck_severity": "Moderate-High"
        }

        return PropagationResponse(
            section_id=section_id,
            total_affected_trains=len(cascaded_details),
            primary_delayed_train="12951",
            cascaded_delays=cascaded_details,
            graph_summary=graph_summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Propagation simulation error: {str(e)}")


@router.post("/whatif", response_model=WhatIfResponse, summary="Simulate Hypothetical Delay Scenario")
def simulate_whatif_scenario(request: WhatIfRequest):
    try:
        pipeline_result = run_railflow_pipeline(
            train_id=request.train_id,
            current_station="NDLS",
            current_delay_min=10.0,
            hypothetical_added_delay=request.additional_delay_minutes
        )

        cascaded_details = [
            CascadedTrainDetail(**item) for item in pipeline_result["cascade_impacts"]
        ]

        total_net_delay = sum(item["additional_cascade_delay_min"] for item in pipeline_result["cascade_impacts"]) + request.additional_delay_minutes

        return WhatIfResponse(
            target_train_id=request.train_id,
            applied_additional_delay_min=request.additional_delay_minutes,
            section_id=request.section_id or "SEC_NDLS_CNB",
            total_downstream_trains_affected=len(cascaded_details),
            network_delay_increase_min=round(total_net_delay, 2),
            affected_trains=cascaded_details
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"WhatIf simulation error: {str(e)}")


@router.get("/network/health", response_model=NetworkHealthResponse, summary="Get Aggregate Network Health")
def get_network_health():
    return NetworkHealthResponse(
        timestamp=datetime.now().isoformat(),
        total_active_trains=142,
        network_punctuality_rate_pct=84.5,
        average_delay_minutes=14.2,
        overall_congestion_index=0.48,
        top_congested_sections=[
            SectionCongestionOverview(
                section_id="SEC_NDLS_CNB",
                congestion_score=0.82,
                active_trains_count=8,
                average_speed_kmh=42.0,
                status="Congested / Bottleneck"
            ),
            SectionCongestionOverview(
                section_id="SEC_CNB_PRYJ",
                congestion_score=0.74,
                active_trains_count=6,
                average_speed_kmh=51.0,
                status="Moderate Traffic"
            ),
            SectionCongestionOverview(
                section_id="SEC_KOTA_RTM",
                congestion_score=0.68,
                active_trains_count=5,
                average_speed_kmh=65.0,
                status="Moderate Traffic"
            )
        ],
        high_risk_corridors=[
            "Delhi - Kanpur Trunk Corridor",
            "Howrah - Asansol Industrial Belt",
            "Mumbai - Kalyan Junction Throat"
        ]
    )


@router.get("/alternatives/{train_id}", summary="Root-Cause Delay Explainer & Smart Alternative Routes")
def get_alternative_trains_route(
    train_id: str = APIPath(..., description="Train number e.g. 12951 or 12424")
):
    """
    GET /alternatives/{train_id}
    Executes Root-Cause Analysis (conflict vs operational) and searches for DIRECT
    and CHAINED multi-leg alternatives when delay > 30 minutes.
    """
    try:
        pipeline_res = run_railflow_pipeline(train_id=train_id)
        graph = pipeline_res.get("graph")
        return evaluate_train_alternatives(train_id=train_id, graph=graph)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating alternatives: {str(e)}")
