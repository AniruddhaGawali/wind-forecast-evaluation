from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from app.config import ACTUALS_FILE, FORECASTS_FILE


@dataclass(frozen=True)
class DataStore:
    actuals: pd.DataFrame
    forecasts: pd.DataFrame


def load_data(
    actuals_file: Path = ACTUALS_FILE, forecasts_file: Path = FORECASTS_FILE
) -> DataStore:
    """Read both saved files once. Fail early with a clear message if one is missing."""
    for path in (actuals_file, forecasts_file):
        if not path.exists():
            raise FileNotFoundError(
                f"Data file {path} not found. Run `uv run python -m app.services.ingest --refresh` first."
            )
    return DataStore(pd.read_parquet(actuals_file), pd.read_parquet(forecasts_file))
