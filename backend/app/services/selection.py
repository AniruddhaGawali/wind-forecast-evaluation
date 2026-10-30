"""Pick, for each target hour, the forecast a buyer would have had at the decision cutoff.

Pure functions: DataFrames in, DataFrames out. No files, no network, no web code.
"""

import re
from dataclasses import dataclass
from datetime import date, time, timedelta

import pandas as pd

from app.config import UK_TZ

_CUTOFF_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


def parse_cutoff(value: str) -> time:
    """'09:00' -> time(9, 0). Raises ValueError on anything that is not a valid HH:MM."""
    match = _CUTOFF_RE.match(value)
    if not match:
        raise ValueError(f"Cutoff must be HH:MM (00:00 to 23:59), got {value!r}.")
    return time(int(match.group(1)), int(match.group(2)))


def expected_hours(start: date, end: date) -> pd.DatetimeIndex:
    """Every target hour (UTC) whose UK delivery day is in [start, end], inclusive."""
    lo = pd.Timestamp(start).tz_localize(UK_TZ)
    hi = pd.Timestamp(end + timedelta(days=1)).tz_localize(UK_TZ)
    return pd.date_range(lo, hi, freq="1h", inclusive="left").tz_convert("UTC")


def cutoff_for_targets(start_times: pd.Series, cutoff: time) -> pd.Series:
    """For each target time, the UTC deadline: the day before its UK delivery day, at `cutoff` UK time."""
    delivery_day = start_times.dt.tz_convert(UK_TZ).dt.tz_localize(None).dt.normalize()
    decision_local = (
        delivery_day
        - pd.Timedelta(days=1)
        + pd.Timedelta(hours=cutoff.hour, minutes=cutoff.minute)
    )
    return decision_local.dt.tz_localize(
        UK_TZ, ambiguous="NaT", nonexistent="shift_forward"
    ).dt.tz_convert("UTC")


def select_forecasts(forecasts: pd.DataFrame, cutoff: time) -> pd.DataFrame:
    """Latest forecast per target hour published at or before that hour's cutoff.

    Returns columns: start_time, publish_time, forecast_mw, horizon_h.
    Target hours with no eligible forecast are simply absent (the caller counts them).
    """
    deadline = cutoff_for_targets(forecasts["start_time"], cutoff)
    eligible = forecasts[
        forecasts["publish_time"] <= deadline
    ]  # never use a forecast from the future
    chosen = (
        eligible.sort_values("publish_time")
        .groupby("start_time", as_index=False)
        .last()
        .rename(columns={"generation_mw": "forecast_mw"})
    )
    chosen["horizon_h"] = (
        chosen["start_time"] - chosen["publish_time"]
    ).dt.total_seconds() / 3600
    return chosen[["start_time", "publish_time", "forecast_mw", "horizon_h"]]


def hourly_actuals(actuals: pd.DataFrame) -> pd.DataFrame:
    """Average the two half-hours inside each hour (alignment option B).

    An hour with only one half-hour present is dropped rather than guessed.
    Returns columns: start_time, actual_mw.
    """
    hour = actuals["start_time"].dt.floor("1h")
    grouped = actuals.groupby(hour)["generation_mw"].agg(["mean", "count"])
    complete = grouped[grouped["count"] == 2]
    return pd.DataFrame(
        {"start_time": complete.index, "actual_mw": complete["mean"].to_numpy()}
    )


@dataclass(frozen=True)
class Coverage:
    expected: int
    scored: int
    missing_forecast: int
    missing_actual: int

    @property
    def skipped(self) -> int:
        return self.expected - self.scored


def build_scored(
    actuals: pd.DataFrame, forecasts: pd.DataFrame, cutoff: time, start: date, end: date
) -> tuple[pd.DataFrame, Coverage]:
    """Join chosen forecasts with hourly actuals for every expected hour and compute the error.

    Returns one row per scored hour (both values present) with columns:
    start_time, publish_time, horizon_h, forecast_mw, actual_mw, error_mw, abs_error_mw.
    """
    hours = pd.DataFrame({"start_time": expected_hours(start, end)})
    chosen = select_forecasts(forecasts, cutoff)
    merged = hours.merge(chosen, on="start_time", how="left").merge(
        hourly_actuals(actuals), on="start_time", how="left"
    )

    has_forecast = merged["forecast_mw"].notna()
    has_actual = merged["actual_mw"].notna()
    scored = merged[has_forecast & has_actual].copy()
    scored["error_mw"] = (
        scored["forecast_mw"] - scored["actual_mw"]
    )  # positive = over-forecast
    scored["abs_error_mw"] = scored["error_mw"].abs()

    coverage = Coverage(
        expected=len(merged),
        scored=len(scored),
        missing_forecast=int((~has_forecast).sum()),
        missing_actual=int((~has_actual).sum()),
    )
    return scored.reset_index(drop=True), coverage
