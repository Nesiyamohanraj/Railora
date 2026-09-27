"""
Pydantic Response Schemas for RailFlow AI
Strictly separates passenger-facing outputs from operator-only graph/debug fields.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ETARange(BaseModel):
    min_eta: str = Field(..., description="10th percentile / earliest predicted arrival time (HH:MM)")
    max_eta: str = Field(..., description="90th percentile / latest predicted arrival time (HH:MM)")
    min_delay_min: float = Field(..., description="10th percentile expected delay in minutes")
    max_delay_min: float = Field(..., description="90th percentile expected delay in minutes")
    expected_delay_min: float = Field(..., description="50th percentile (median) expected delay in minutes")


class CurrentPosition(BaseModel):
    station_code: str
    station_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class AlternativeTrain(BaseModel):
    train_number: str
    train_name: str
    departure_time: str
    arrival_time: str
    historical_reliability_score: float
    expected_delay_min: float


class PassengerPredictResponse(BaseModel):
    """
    Passenger-Facing Output Response
    Excludes raw SHAP matrices, baseline formulas, and operator debug metrics.
    """
    train_name: str = Field(..., description="Full train name")
    train_number: str = Field(..., description="Official train number")
    predicted_eta_range: ETARange = Field(..., description="Quantile uncertainty range (min, max)")
    current_status: str = Field(..., description="Human-readable status e.g. 'On Time' or '25 min late'")
    delay_reason: str = Field(..., description="Plain-language reason derived from SHAP explanations")
    current_position: CurrentPosition = Field(..., description="Current position station and coordinates")
    next_station: str = Field(..., description="Next upcoming station code/name")
    previous_station: str = Field(..., description="Last passed station code/name")
    historical_reliability_score: float = Field(..., description="Score 0-100 indicating train punctuality history")
    confidence_trend: str = Field(..., description="Narrowing indicator e.g. 'Narrowing (High Confidence)' as train nears destination")
    alternative_trains: List[AlternativeTrain] = Field(
        default_factory=list,
        description="Populated only when train delay is significant (>20 minutes)"
    )


class CascadedTrainDetail(BaseModel):
    train_id: str
    train_name: str
    original_delay_min: float
    additional_cascade_delay_min: float
    new_projected_delay_min: float
    dependency_reason: str


class PropagationResponse(BaseModel):
    """
    Operator-Facing Response for Delay Cascade Analysis
    """
    section_id: str
    total_affected_trains: int
    primary_delayed_train: str
    cascaded_delays: List[CascadedTrainDetail]
    graph_summary: Dict[str, Any]


class WhatIfResponse(BaseModel):
    """
    Operator-Facing Response for Scenario Simulator
    """
    target_train_id: str
    applied_additional_delay_min: float
    section_id: str
    total_downstream_trains_affected: int
    network_delay_increase_min: float
    affected_trains: List[CascadedTrainDetail]


class SectionCongestionOverview(BaseModel):
    section_id: str
    congestion_score: float
    active_trains_count: int
    average_speed_kmh: float
    status: str


class NetworkHealthResponse(BaseModel):
    """
    Operator-Facing Response for Overall Network Status
    """
    timestamp: str
    total_active_trains: int
    network_punctuality_rate_pct: float
    average_delay_minutes: float
    overall_congestion_index: float
    top_congested_sections: List[SectionCongestionOverview]
    high_risk_corridors: List[str]
