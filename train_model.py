"""
Standalone Offline Model Training Script — RailFlow AI
Loads historical schedule & station data, extracts features, trains XGBoost model,
and exports model weights to data/xgb_model.json.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import logging

from app.config import BASE_DIR, DATA_DIR, MODEL_PATH, PRIMARY_TRAIN_DETAILS_CSV, COMBINED_SCHEDULE_CSV
from app.pipeline.features import extract_features, features_to_matrix, FEATURE_COLUMNS
from app.pipeline.model import train_initial_xgboost_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("train_model")


def train_and_save():
    logger.info("Starting RailFlow AI XGBoost Offline Training...")

    model = train_initial_xgboost_model()

    logger.info(f"Successfully trained and saved model weights to {MODEL_PATH}")


if __name__ == "__main__":
    train_and_save()
