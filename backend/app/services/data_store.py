from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from app.config import ACTUALS_FILE, FORECASTS_FILE

ACTUAL_COLUMNS = {"start_time", "generation_mw"}
FORECAST_COLUMNS = {"start_time", "publish_time", "generation_mw"}

_REFRESH_HINT = "Run `uv run python -m app.services.ingest --refresh` first."


@dataclass(frozen=True)
class DataStore:
    actuals: pd.DataFrame
    forecasts: pd.DataFrame


def _read(path: Path, columns: set[str]) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Data file {path} not found. {_REFRESH_HINT}")
    df = pd.read_parquet(path)
    missing = columns - set(df.columns)
    if missing:
        raise ValueError(
            f"Data file {path} is missing columns {sorted(missing)}. {_REFRESH_HINT}"
        )
    if df.empty:
        raise ValueError(f"Data file {path} has no rows. {_REFRESH_HINT}")
    return df


def load_data(
    actuals_file: Path = ACTUALS_FILE, forecasts_file: Path = FORECASTS_FILE
) -> DataStore:
    """Read both saved files once. Fail early with a clear message if one is missing, empty or malformed."""
    return DataStore(
        _read(actuals_file, ACTUAL_COLUMNS), _read(forecasts_file, FORECAST_COLUMNS)
    )
