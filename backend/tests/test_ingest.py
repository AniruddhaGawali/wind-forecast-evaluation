from datetime import date
from itertools import pairwise

import pandas as pd

from app.services.elexon_client import _date_chunks
from app.services.ingest import clean_actuals, clean_forecasts, validation_report


def test_clean_actuals_keeps_wind_utc_and_dedupes() -> None:
    rows = [
        {"startTime": "2026-01-02T00:30:00Z", "fuelType": "WIND", "generation": 10},
        {"startTime": "2026-01-02T00:00:00Z", "fuelType": "WIND", "generation": 5},
        {"startTime": "2026-01-02T00:00:00Z", "fuelType": "WIND", "generation": 6},
        {"startTime": "2026-01-02T00:00:00Z", "fuelType": "CCGT", "generation": 99},
        {"startTime": "2026-01-02T01:00:00Z", "fuelType": "WIND", "generation": None},
    ]
    df = clean_actuals(rows)
    assert list(df.columns) == ["start_time", "generation_mw"]
    assert str(df["start_time"].dt.tz) == "UTC"
    assert df["generation_mw"].tolist() == [6, 10]
    assert df["start_time"].is_monotonic_increasing


def test_clean_forecasts_dedupes_on_target_and_publish_time() -> None:
    rows = [
        {
            "startTime": "2026-01-02T12:00:00Z",
            "publishTime": "2026-01-01T11:30:00Z",
            "generation": 1,
        },
        {
            "startTime": "2026-01-02T12:00:00Z",
            "publishTime": "2026-01-01T11:30:00Z",
            "generation": 1,
        },
        {
            "startTime": "2026-01-02T12:00:00Z",
            "publishTime": "2026-01-01T15:30:00Z",
            "generation": 2,
        },
    ]
    df = clean_forecasts(rows)
    assert len(df) == 2
    assert df["publish_time"].tolist() == sorted(df["publish_time"].tolist())


def test_date_chunks_cover_range_without_overlap() -> None:
    chunks = list(_date_chunks(date(2026, 1, 2), date(2026, 2, 1)))
    assert chunks[0][0] == date(2026, 1, 2)
    assert chunks[-1][1] == date(2026, 2, 1)
    for (_, prev_end), (next_start, _) in pairwise(chunks):
        assert (next_start - prev_end).days == 1


def test_validation_report_flags_gap_and_negative() -> None:
    times = pd.to_datetime(["2026-01-02T00:00:00Z", "2026-01-02T01:00:00Z"], utc=True)
    actuals = pd.DataFrame({"start_time": times, "generation_mw": [-1.0, 5.0]})
    forecasts = pd.DataFrame(
        {
            "start_time": times,
            "publish_time": times - pd.Timedelta(hours=24),
            "generation_mw": [1.0, 2.0],
        }
    )
    report = validation_report(actuals, forecasts)
    assert "missing half-hours: 1" in report
    assert "negative values: 1" in report
