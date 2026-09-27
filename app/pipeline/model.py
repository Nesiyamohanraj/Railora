"""
Core ML Model Module — RailFlow AI
Implements XGBoost / LightGBM model loader, trainer, and predictor.
Predicts ML additional delay (beyond baseline delay).
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional
from pathlib import Path
import logging

try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

from app.config import MODEL_PATH
from app.pipeline.features import FEATURE_COLUMNS, features_to_matrix

logger = logging.getLogger(__name__)

_XGB_MODEL: Optional[Any] = None


def get_or_train_model():
    """
    Returns loaded XGBoost model.
    If no saved model binary exists, trains a initial model on baseline domain physics.
    """
    global _XGB_MODEL
    if _XGB_MODEL is not None:
        return _XGB_MODEL

    if MODEL_PATH.exists() and XGB_AVAILABLE:
        try:
            model = xgb.XGBRegressor()
            model.load_model(str(MODEL_PATH))
            _XGB_MODEL = model
            logger.info(f"Loaded trained XGBoost model from {MODEL_PATH}")
            return _XGB_MODEL
        except Exception as e:
            logger.warning(f"Could not load XGBoost model from {MODEL_PATH}: {e}")

    # Fallback / Initial training on domain physics synthetic training dataset
    _XGB_MODEL = train_initial_xgboost_model()
    return _XGB_MODEL


def train_initial_xgboost_model() -> Any:
    """
    Trains a lightweight initial XGBoost regressor model on synthesized domain physics dataset.
    Features:
    [current_delay, speed_ratio, trains_ahead, weather_severity_score, congestion_score, day_type_code, dwell_time_pattern, historical_section_delay_rate]
    """
    np.random.seed(42)
    n_samples = 2500

    current_delay = np.random.exponential(scale=20.0, size=n_samples)
    speed_ratio = np.random.uniform(0.4, 1.2, size=n_samples)
    trains_ahead = np.random.randint(0, 6, size=n_samples)
    weather_severity = np.random.choice([0.0, 0.1, 0.3, 0.7, 0.95], size=n_samples, p=[0.5, 0.2, 0.15, 0.1, 0.05])
    congestion_score = np.random.uniform(0.1, 0.95, size=n_samples)
    day_type_code = np.random.choice([0, 1, 2], size=n_samples, p=[0.7, 0.2, 0.1])
    dwell_time_pattern = np.random.normal(2.0, 3.0, size=n_samples)
    hist_delay_rate = np.random.uniform(5.0, 25.0, size=n_samples)

    # Domain equation for target additional delay:
    # Heavy weather (+15m), high congestion (+20m), trains ahead (+5m each), slow speed ratio (+10m)
    y_additional_delay = (
        (1.0 - speed_ratio) * 15.0 +
        trains_ahead * 4.5 +
        weather_severity * 22.0 +
        congestion_score * 25.0 +
        day_type_code * 3.5 +
        np.maximum(0, dwell_time_pattern) * 0.8 +
        hist_delay_rate * 0.4 +
        np.random.normal(0, 2.5, size=n_samples)
    )
    y_additional_delay = np.maximum(0.0, y_additional_delay)

    X = np.column_stack([
        current_delay, speed_ratio, trains_ahead, weather_severity,
        congestion_score, day_type_code, dwell_time_pattern, hist_delay_rate
    ])

    if XGB_AVAILABLE:
        model = xgb.XGBRegressor(
            n_estimators=100,
            learning_rate=0.08,
            max_depth=5,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )
        model.fit(X, y_additional_delay)

        # Save model
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        try:
            model.save_model(str(MODEL_PATH))
            logger.info(f"Saved initial trained XGBoost model to {MODEL_PATH}")
        except Exception as e:
            logger.warning(f"Could not save XGBoost model to disk: {e}")
        return model
    else:
        # Fallback linear surrogate if XGBoost is missing
        class DummyLinearModel:
            def predict(self, X_mat):
                # Simple weighted dot product
                weights = np.array([0.05, -12.0, 4.0, 20.0, 22.0, 3.0, 0.7, 0.3], dtype=np.float32)
                preds = np.dot(X_mat, weights)
                return np.maximum(0.0, preds)
        return DummyLinearModel()


def predict_additional_delay(feature_dict: Dict[str, Any]) -> float:
    """
    Runs feature vector through XGBoost model to predict additional delay in minutes.
    """
    model = get_or_train_model()
    X_mat = features_to_matrix(feature_dict)

    if hasattr(model, "predict"):
        preds = model.predict(X_mat)
        additional_delay = float(preds[0])
    else:
        additional_delay = 5.0

    return round(max(0.0, additional_delay), 2)
