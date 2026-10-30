"""All settings in one place. The deployment-specific ones can be overridden with environment variables."""

import os
from datetime import UTC, date, datetime
from pathlib import Path

ELEXON_BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"

# Folder holding actuals.parquet and forecasts.parquet. Override with WIND_DATA_DIR.
DATA_DIR = Path(
    os.environ.get("WIND_DATA_DIR", Path(__file__).resolve().parent.parent / "data")
)
ACTUALS_FILE = DATA_DIR / "actuals.parquet"
FORECASTS_FILE = DATA_DIR / "forecasts.parquet"

# Delivery window: decisions made 1 Jan..31 Jan are for delivery 2 Jan..1 Feb.
DELIVERY_START = date(2026, 1, 2)
DELIVERY_END = date(2026, 2, 1)

# Forecasts for the first delivery days were published earlier, so start fetching a few days before.
FORECAST_PUBLISH_START = datetime(2025, 12, 29, tzinfo=UTC)
FORECAST_PUBLISH_END = datetime(2026, 2, 1, tzinfo=UTC)

CHUNK_DAYS = 7
REQUEST_TIMEOUT_S = 30.0
MAX_RETRIES = 3

# Decision time on D-1 (UK time) used when a request gives none. Override with WIND_DEFAULT_CUTOFF.
DEFAULT_CUTOFF = os.environ.get("WIND_DEFAULT_CUTOFF", "09:00")

# Browser origins allowed to call the API, comma separated. Override with WIND_ALLOWED_ORIGINS.
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "WIND_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]

LOG_LEVEL = os.environ.get("WIND_LOG_LEVEL", "INFO")

# Delivery days and the decision cutoff are defined in UK local time, then converted to UTC.
UK_TZ = "Europe/London"
SENSITIVITY_CUTOFFS = ["06:00", "09:00", "10:00", "12:00", "18:00"]
MAX_SENSITIVITY_CUTOFFS = 12

# How many (cutoff, start, end) analysis results to keep in memory.
SCORED_CACHE_SIZE = 128
