"""Error statistics on the scored hours. Pure functions, no web or file code."""

import math
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from app.config import UK_TZ

HORIZON_BINS = [0, 12, 24, 36, 48, math.inf]
HORIZON_LABELS = ["0-12h", "12-24h", "24-36h", "36-48h", "48h+"]
LEVEL_BINS = [0, 5_000, 10_000, 15_000, math.inf]
LEVEL_LABELS = ["0-5 GW", "5-10 GW", "10-15 GW", "15 GW+"]

# Below this total actual output (MW summed over the hours), a percentage error is meaningless.
WAPE_MIN_ACTUAL_MW = 1.0


@dataclass(frozen=True)
class Summary:
    n: int
    mae: float | None
    rmse: float | None
    bias: float | None
    p50: float | None
    p90: float | None
    p95: float | None
    wape_pct: float | None

    def as_dict(self) -> dict[str, float | int | None]:
        return asdict(self)


def percentile(values: pd.Series, q: float) -> float | None:
    """Nearest-rank percentile: the value at position ceil(q * n) in the sorted list (1-based)."""
    if values.empty:
        return None
    return float(np.percentile(values.to_numpy(), q * 100, method="inverted_cdf"))


def summarise(scored: pd.DataFrame) -> Summary:
    n = len(scored)
    if n == 0:
        return Summary(0, None, None, None, None, None, None, None)
    error = scored["error_mw"]
    abs_error = scored["abs_error_mw"]
    actual_total = scored["actual_mw"].sum()
    return Summary(
        n=n,
        mae=float(abs_error.mean()),
        rmse=float(np.sqrt((error**2).mean())),
        bias=float(error.mean()),
        p50=percentile(abs_error, 0.50),
        p90=percentile(abs_error, 0.90),
        p95=percentile(abs_error, 0.95),
        wape_pct=float(abs_error.sum() / actual_total * 100)
        if actual_total >= WAPE_MIN_ACTUAL_MW
        else None,
    )


def breakdown(
    scored: pd.DataFrame, key: pd.Series, name: str
) -> list[dict[str, object]]:
    """Summary per group, as plain dicts: [{name: group, n, mae, rmse, bias, ...}, ...]. Empty groups are left out."""
    rows: list[dict[str, object]] = []
    for group, part in scored.groupby(key, observed=True, sort=True):
        rows.append({name: group, **summarise(part).as_dict()})
    return rows


def by_hour_of_day(scored: pd.DataFrame) -> list[dict[str, object]]:
    """Grouped by the UTC hour of the target time (0 to 23)."""
    return breakdown(scored, scored["start_time"].dt.hour, "hour")


def by_day(scored: pd.DataFrame) -> list[dict[str, object]]:
    delivery_day = scored["start_time"].dt.tz_convert(UK_TZ).dt.strftime("%Y-%m-%d")
    return breakdown(scored, delivery_day, "day")


def by_horizon(scored: pd.DataFrame) -> list[dict[str, object]]:
    bucket = pd.cut(
        scored["horizon_h"], HORIZON_BINS, labels=HORIZON_LABELS, right=False
    )
    return breakdown(scored, bucket, "horizon")


def by_generation_level(scored: pd.DataFrame) -> list[dict[str, object]]:
    bucket = pd.cut(scored["actual_mw"], LEVEL_BINS, labels=LEVEL_LABELS, right=False)
    return breakdown(scored, bucket, "level")


def buffer_mw(p90: float | None) -> int | None:
    """The P90 absolute error rounded UP to a whole MW: a safety buffer should never be rounded down."""
    return None if p90 is None else math.ceil(p90)


def recommendation_text(p90: float | None) -> str:
    buffer = buffer_mw(p90)
    if buffer is None:
        return "Not enough data to recommend a buffer."
    return f"Keep a buffer of about {buffer:,} MW to cover 90% of forecast errors."


HISTOGRAM_BIN_MW = 500


def error_histogram(
    scored: pd.DataFrame, bin_mw: int = HISTOGRAM_BIN_MW
) -> list[dict[str, float | int]]:
    """Count signed errors in fixed-width bins: [{lo, hi, count}], from the lowest to the highest bin used.

    A value exactly on a boundary goes into the bin that starts there (lo <= error < hi).
    """
    if scored.empty:
        return []
    errors = scored["error_mw"]
    first = math.floor(errors.min() / bin_mw)
    last = math.floor(errors.max() / bin_mw)
    counts = (errors // bin_mw).astype(int).value_counts()
    return [
        {
            "lo": float(i * bin_mw),
            "hi": float((i + 1) * bin_mw),
            "count": int(counts.get(i, 0)),
        }
        for i in range(first, last + 1)
    ]
