import math

import pandas as pd
import pytest

from app.services import metrics


def scored(
    errors: list[float], actual: float = 1000.0, horizon_h: float = 20.0
) -> pd.DataFrame:
    n = len(errors)
    times = pd.date_range("2026-01-02T00:00:00Z", periods=n, freq="1h")
    return pd.DataFrame(
        {
            "start_time": times,
            "actual_mw": [actual] * n,
            "forecast_mw": [actual + e for e in errors],
            "error_mw": errors,
            "abs_error_mw": [abs(e) for e in errors],
            "horizon_h": [horizon_h] * n,
        }
    )


def test_summary_matches_hand_calculation() -> None:
    # errors 100, -200, 300, 400 against actual 1000 each
    s = metrics.summarise(scored([100, -200, 300, 400]))
    assert s.n == 4
    assert s.mae == 250  # (100 + 200 + 300 + 400) / 4
    assert s.rmse == pytest.approx(
        math.sqrt((100**2 + 200**2 + 300**2 + 400**2) / 4)
    )  # 273.86
    assert s.bias == 150  # (100 - 200 + 300 + 400) / 4
    assert s.p50 == 200  # sorted |e| = 100, 200, 300, 400; position ceil(0.5 * 4) = 2
    assert s.p90 == 400  # position ceil(0.9 * 4) = 4
    assert s.p95 == 400
    assert s.wape_pct == 25  # 1000 / 4000 * 100


def test_percentile_nearest_rank_on_ten_values() -> None:
    values = pd.Series([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    assert metrics.percentile(values, 0.90) == 90  # position ceil(9.0) = 9
    assert metrics.percentile(values, 0.95) == 100  # position ceil(9.5) = 10
    assert metrics.percentile(values, 0.50) == 50


def test_empty_input_gives_no_numbers() -> None:
    s = metrics.summarise(scored([]))
    assert s.n == 0
    assert s.mae is None and s.p90 is None and s.wape_pct is None
    assert (
        metrics.recommendation_text(s.p90) == "Not enough data to recommend a buffer."
    )


def test_wape_guard_for_zero_actual() -> None:
    assert metrics.summarise(scored([5, -5], actual=0.0)).wape_pct is None


def test_breakdown_by_horizon_and_level() -> None:
    df = pd.concat(
        [scored([100], horizon_h=5), scored([300, 300], actual=12_000, horizon_h=30)]
    )
    horizon = {row["horizon"]: row for row in metrics.by_horizon(df)}
    assert set(horizon) == {"0-12h", "24-36h"}  # empty buckets are left out
    assert horizon["24-36h"]["n"] == 2 and horizon["24-36h"]["mae"] == 300
    levels = {row["level"]: row["n"] for row in metrics.by_generation_level(df)}
    assert levels == {"0-5 GW": 1, "10-15 GW": 2}


def test_breakdown_by_hour_and_day() -> None:
    df = scored([10] * 26)  # 26 hours from 2 Jan 00:00 UTC
    hours = metrics.by_hour_of_day(df)
    assert [r["n"] for r in hours][:3] == [2, 2, 1]
    days = metrics.by_day(df)
    assert [(r["day"], r["n"]) for r in days] == [("2026-01-02", 24), ("2026-01-03", 2)]


def test_buffer_is_rounded_up() -> None:
    assert metrics.buffer_mw(4098.5) == 4099
    assert metrics.buffer_mw(4098.0) == 4098
    assert metrics.buffer_mw(None) is None
    assert (
        metrics.recommendation_text(4098.5)
        == "Keep a buffer of about 4,099 MW to cover 90% of forecast errors."
    )


def test_error_histogram_bins() -> None:
    # bins of 500 MW: -200 -> [-500, 0); 0 and 499 -> [0, 500); 1200 -> [1000, 1500)
    bins = metrics.error_histogram(scored([-200, 0, 499, 1200]))
    assert bins == [
        {"lo": -500.0, "hi": 0.0, "count": 1},
        {"lo": 0.0, "hi": 500.0, "count": 2},
        {"lo": 500.0, "hi": 1000.0, "count": 0},  # empty bins inside the range are kept
        {"lo": 1000.0, "hi": 1500.0, "count": 1},
    ]
    assert metrics.error_histogram(scored([])) == []
