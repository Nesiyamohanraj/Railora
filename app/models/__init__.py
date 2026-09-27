"""
Pydantic Request and Response Schemas for RailFlow AI
"""
from app.models.request import PredictRequest, WhatIfRequest
from app.models.response import (
    PassengerPredictResponse,
    PropagationResponse,
    WhatIfResponse,
    NetworkHealthResponse,
    AlternativeTrain,
)

__all__ = [
    "PredictRequest",
    "WhatIfRequest",
    "PassengerPredictResponse",
    "PropagationResponse",
    "WhatIfResponse",
    "NetworkHealthResponse",
    "AlternativeTrain",
]
