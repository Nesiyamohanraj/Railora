"""
RailFlow AI Configuration
Strictly uses pathlib.Path for cross-platform (Windows / Linux) compatibility.
"""
from pathlib import Path
import os

# Root directories
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = BASE_DIR / "data"
ARCHIVE_DIR = BASE_DIR / "archive"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Datasets
COMBINED_SCHEDULE_CSV = ARCHIVE_DIR / "combined_schedule.csv"
COMBINED_DELAY_CSV = ARCHIVE_DIR / "combined_delay.csv"
STATION_NAMES_CSV = ARCHIVE_DIR / "station_full_names.csv"
TRAIN_DETAILS_CSV = ARCHIVE_DIR / "train_details.csv"
PRIMARY_TRAIN_DETAILS_CSV = BASE_DIR / "Train_details_22122017.csv"

# Model & Database paths
MODEL_PATH = DATA_DIR / "xgb_model.json"
FEEDBACK_DB_PATH = DATA_DIR / "prediction_feedback.db"

# Third-party External APIs
# NOTE: RailRadar (api.railradar.org) is an unofficial third-party API, not an official government feed.
RAILRADAR_BASE_URL = os.getenv("RAILRADAR_BASE_URL", "https://api.railradar.org")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "demo_key")

# System Defaults
DEFAULT_RECOVERY_FACTOR = 0.15 # NTES recovery buffer factor
DEFAULT_AVG_SPEED_KMH = 55.0   # Default average train speed in km/h
