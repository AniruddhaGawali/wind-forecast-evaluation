"""Download, clean and save the Elexon wind data. Run with `python -m app.services.ingest --refresh`."""

import argparse
import logging
import time

import pandas as pd

from app.config import (
    ACTUALS_FILE,
    DATA_DIR,
    DELIVERY_END,
    DELIVERY_START,
    FORECAST_PUBLISH_END,
    FORECAST_PUBLISH_START,
    FORECASTS_FILE,
)
from app.services import elexon_client

logger = logging.getLogger(__name__)


def clean_actuals(rows: list[elexon_client.Row]) -> pd.DataFrame:
    """Keep WIND rows as (start_time, generation_mw) in UTC, deduplicated and sorted."""
    df = pd.DataFrame(rows, columns=["startTime", "fuelType", "generation"])
    df = df[df["fuelType"] == "WIND"]
    df = pd.DataFrame(
        {
            "start_time": pd.to_datetime(df["startTime"], utc=True),
            "generation_mw": pd.to_numeric(df["generation"], errors="coerce"),
        }
    )
    return _finish(df, ["start_time"])


def clean_forecasts(rows: list[elexon_client.Row]) -> pd.DataFrame:
    """Keep (start_time, publish_time, generation_mw) in UTC, deduplicated and sorted."""
    raw = pd.DataFrame(rows, columns=["startTime", "publishTime", "generation"])
    df = pd.DataFrame(
        {
            "start_time": pd.to_datetime(raw["startTime"], utc=True),
            "publish_time": pd.to_datetime(raw["publishTime"], utc=True),
            "generation_mw": pd.to_numeric(raw["generation"], errors="coerce"),
        }
    )
    return _finish(df, ["start_time", "publish_time"])


def _finish(df: pd.DataFrame, key: list[str]) -> pd.DataFrame:
    df = df.dropna()
    df = df.drop_duplicates(subset=key, keep="last")
    return df.sort_values(key).reset_index(drop=True)


def validation_report(actuals: pd.DataFrame, forecasts: pd.DataFrame) -> str:
    """Human-readable data quality report: counts, gaps, odd values, publish range."""
    lines = ["=== Validation report ==="]

    per_day = actuals.groupby(actuals["start_time"].dt.date).size()
    expected_days = (DELIVERY_END - DELIVERY_START).days + 1
    lines += [
        f"Actuals: {len(actuals)} rows (expected {expected_days * 48})",
        f"  range: {actuals['start_time'].min()} -> {actuals['start_time'].max()}",
        (
            f"  days: {len(per_day)} (expected {expected_days}); "
            f"days without 48 slots: {dict(per_day[per_day != 48]) or 'none'}"
        ),
        f"  missing half-hours: {_count_gaps(actuals['start_time'], '30min')}",
        f"  negative values: {int((actuals['generation_mw'] < 0).sum())}",
        (
            f"  min/mean/max MW: {actuals['generation_mw'].min():.0f} / "
            f"{actuals['generation_mw'].mean():.0f} / {actuals['generation_mw'].max():.0f}"
        ),
        f"Forecasts: {len(forecasts)} rows",
        f"  publish range: {forecasts['publish_time'].min()} -> {forecasts['publish_time'].max()}",
        f"  target range: {forecasts['start_time'].min()} -> {forecasts['start_time'].max()}",
        f"  distinct target hours: {forecasts['start_time'].nunique()}",
        f"  forecasts per target hour (median): {forecasts.groupby('start_time').size().median():.0f}",
        f"  negative values: {int((forecasts['generation_mw'] < 0).sum())}",
        f"  published after own target time: {int((forecasts['publish_time'] > forecasts['start_time']).sum())}",
    ]
    return "\n".join(lines)


def _count_gaps(times: pd.Series, freq: str) -> int:
    full = pd.date_range(times.min(), times.max(), freq=freq)
    return len(full.difference(pd.DatetimeIndex(times)))


def download() -> tuple[pd.DataFrame, pd.DataFrame]:
    started = time.perf_counter()
    with elexon_client.make_client() as client:
        actual_rows = elexon_client.fetch_actuals(client, DELIVERY_START, DELIVERY_END)
        forecast_rows = elexon_client.fetch_forecasts(
            client, FORECAST_PUBLISH_START, FORECAST_PUBLISH_END
        )
    logger.info(
        "Downloaded %d actual and %d forecast rows in %.1fs",
        len(actual_rows),
        len(forecast_rows),
        time.perf_counter() - started,
    )
    return clean_actuals(actual_rows), clean_forecasts(forecast_rows)


def save(actuals: pd.DataFrame, forecasts: pd.DataFrame) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    actuals.to_parquet(ACTUALS_FILE, index=False)
    forecasts.to_parquet(FORECASTS_FILE, index=False)
    logger.info("Saved %s and %s", ACTUALS_FILE, FORECASTS_FILE)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh", action="store_true", help="re-download even if data files exist"
    )
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    if args.refresh or not (ACTUALS_FILE.exists() and FORECASTS_FILE.exists()):
        actuals, forecasts = download()
        save(actuals, forecasts)
    else:
        logger.info(
            "Data files exist; use --refresh to re-download. Validating existing files."
        )
        actuals, forecasts = (
            pd.read_parquet(ACTUALS_FILE),
            pd.read_parquet(FORECASTS_FILE),
        )
    print(validation_report(actuals, forecasts))


if __name__ == "__main__":
    main()
