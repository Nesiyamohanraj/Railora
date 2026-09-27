"""
Data Ingestion Module — RailFlow AI
Pulls from RailRadar (or fallback replay), historical IR datasets, and weather API.
Normalizes data into unified schema:
train_id, timestamp, station, scheduled_time, actual_time, delay_minutes, weather_tag, section_id, section_type, day_type
"""
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional

from app.config import (
    PRIMARY_TRAIN_DETAILS_CSV,
    COMBINED_SCHEDULE_CSV,
    STATION_NAMES_CSV,
    TRAIN_DETAILS_CSV,
)

# In-memory cached dataframes for fast API lookup
_SCHEDULE_DF: Optional[pd.DataFrame] = None
_STATION_DF: Optional[pd.DataFrame] = None
_TRAIN_META_DF: Optional[pd.DataFrame] = None


def load_raw_datasets():
    """Loads historical CSV datasets using pathlib.Path for cross-platform support."""
    global _SCHEDULE_DF, _STATION_DF, _TRAIN_META_DF

    if _SCHEDULE_DF is not None:
        return _SCHEDULE_DF, _STATION_DF, _TRAIN_META_DF

    # Station Metadata
    if STATION_NAMES_CSV.exists():
        _STATION_DF = pd.read_csv(STATION_NAMES_CSV)
    else:
        _STATION_DF = pd.DataFrame(columns=["station_name", "station_full_name", "station_zone"])

    # Train Metadata
    if TRAIN_DETAILS_CSV.exists():
        _TRAIN_META_DF = pd.read_csv(TRAIN_DETAILS_CSV, dtype={"train_no": str})
    else:
        _TRAIN_META_DF = pd.DataFrame(columns=["train_no", "train_name", "type_code"])

    # Combined Schedule Data
    if COMBINED_SCHEDULE_CSV.exists():
        _SCHEDULE_DF = pd.read_csv(COMBINED_SCHEDULE_CSV, dtype={"train_no": str})
    elif PRIMARY_TRAIN_DETAILS_CSV.exists():
        df_raw = pd.read_csv(PRIMARY_TRAIN_DETAILS_CSV, dtype={"Train No": str})
        _SCHEDULE_DF = df_raw.rename(columns={
            "Train No": "train_no",
            "Train Name": "train_name",
            "SEQ": "station_no",
            "Station Code": "station_name",
            "Arrival time": "arrival_time",
            "Departure Time": "departure_time",
            "Distance": "distance_from_origin"
        })
    else:
        _SCHEDULE_DF = pd.DataFrame()

    return _SCHEDULE_DF, _STATION_DF, _TRAIN_META_DF


def join_historical_weather(delay_records: pd.DataFrame, weather_records: pd.DataFrame) -> pd.DataFrame:
    """
    Joins historical weather records to delay records on (station, timestamp_hour).
    Ensures pre-join optimization across historical train data.
    """
    if delay_records.empty:
        return delay_records

    if weather_records.empty:
        delay_records["weather_tag"] = "clear"
        return delay_records

    # Truncate timestamp to hour key for joining
    delay_records["join_key_time"] = pd.to_datetime(delay_records["timestamp"]).dt.floor("h")
    weather_records["join_key_time"] = pd.to_datetime(weather_records["timestamp"]).dt.floor("h")

    merged = pd.merge(
        delay_records,
        weather_records[["station", "join_key_time", "weather_tag"]],
        on=["station", "join_key_time"],
        how="left"
    )
    merged["weather_tag"] = merged["weather_tag"].fillna("clear")
    merged.drop(columns=["join_key_time"], inplace=True, errors="ignore")
    return merged


def normalize_record(raw_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a single train status observation into the unified RailFlow schema:
    - train_id
    - timestamp
    - station
    - scheduled_time
    - actual_time
    - delay_minutes
    - weather_tag
    - section_id
    - section_type
    - day_type
    """
    now = datetime.now()

    train_id = str(raw_record.get("train_id") or raw_record.get("train_no") or "12951")
    station = str(raw_record.get("station") or raw_record.get("station_name") or "NDLS")
    timestamp = raw_record.get("timestamp") or now.isoformat()

    scheduled_time = raw_record.get("scheduled_time") or "12:00"
    actual_time = raw_record.get("actual_time") or scheduled_time
    delay_minutes = float(raw_record.get("delay_minutes") if raw_record.get("delay_minutes") is not None else 0.0)

    weather_tag = str(raw_record.get("weather_tag") or "clear")
    next_stn = str(raw_record.get("next_station") or "CNB")
    section_id = raw_record.get("section_id") or f"SEC_{station}_{next_stn}"
    section_type = raw_record.get("section_type") or ("junction" if "JN" in station or "JN" in next_stn else "trunk")

    day_of_week = now.weekday()
    day_type = raw_record.get("day_type") or ("weekend" if day_of_week >= 5 else "weekday")

    return {
        "train_id": train_id,
        "train_name": raw_record.get("train_name", f"Express {train_id}"),
        "timestamp": timestamp,
        "station": station,
        "scheduled_time": scheduled_time,
        "actual_time": actual_time,
        "delay_minutes": delay_minutes,
        "weather_tag": weather_tag,
        "section_id": section_id,
        "section_type": section_type,
        "day_type": day_type,
        "next_station": next_stn,
        "previous_station": raw_record.get("previous_station", "ORIGIN"),
        "distance_covered_km": float(raw_record.get("distance_covered_km") or 150.0),
        "total_route_km": float(raw_record.get("total_route_km") or 1380.0),
    }
