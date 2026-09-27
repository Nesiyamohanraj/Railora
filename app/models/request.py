"""
Pydantic Request Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional


class PredictRequest(BaseModel):
    train_id: str = Field(..., description="Train number or ID (e.g., '12951' or '01021')")
    current_station: str = Field(..., description="Current station code (e.g., 'NDLS' or 'KOTA')")
    current_delay_minutes: Optional[float] = Field(0.0, description="Reported current delay in minutes")
    departure_timestamp: Optional[str] = Field(None, description="ISO timestamp or time string HH:MM")


class WhatIfRequest(BaseModel):
    train_id: str = Field(..., description="Target train ID to apply hypothetical delay")
    additional_delay_minutes: float = Field(..., description="Hypothetical added delay in minutes (e.g. 15.0)")
    section_id: Optional[str] = Field(None, description="Optional section ID where delay occurs")
