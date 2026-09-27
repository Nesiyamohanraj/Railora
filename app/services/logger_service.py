"""
Prediction Feedback Logger Service — RailFlow AI
Logs predictions vs actual arrival outcomes into an SQLite database for model evaluation & retraining.
"""
import sqlite3
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from app.config import FEEDBACK_DB_PATH

logger = logging.getLogger(__name__)


def init_feedback_db():
    """Initializes SQLite database and predictions_log table."""
    try:
        conn = sqlite3.connect(FEEDBACK_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                train_id TEXT NOT NULL,
                station_code TEXT NOT NULL,
                baseline_delay_min REAL,
                ml_predicted_delay_min REAL,
                total_predicted_delay_min REAL,
                actual_delay_min REAL,
                weather_tag TEXT,
                congestion_score REAL,
                delay_reason TEXT
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error initializing feedback database: {e}")


def log_prediction_event(
    train_id: str,
    station_code: str,
    baseline_delay_min: float,
    ml_predicted_delay_min: float,
    total_predicted_delay_min: float,
    weather_tag: str = "clear",
    congestion_score: float = 0.4,
    delay_reason: str = ""
):
    """Logs a newly made prediction for retrospective validation."""
    try:
        init_feedback_db()
        conn = sqlite3.connect(FEEDBACK_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions_log (
                timestamp, train_id, station_code, baseline_delay_min,
                ml_predicted_delay_min, total_predicted_delay_min,
                actual_delay_min, weather_tag, congestion_score, delay_reason
            ) VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            train_id,
            station_code,
            baseline_delay_min,
            ml_predicted_delay_min,
            total_predicted_delay_min,
            weather_tag,
            congestion_score,
            delay_reason
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Could not log prediction to SQLite: {e}")


def update_actual_outcome(log_id: int, actual_delay_min: float):
    """Updates actual delay outcome when train arrives at destination."""
    try:
        conn = sqlite3.connect(FEEDBACK_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE predictions_log SET actual_delay_min = ? WHERE id = ?
        """, (actual_delay_min, log_id))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Could not update actual outcome in SQLite: {e}")
