from datetime import date, time

import pandas as pd
import pytest

from app.config import DELIVERY_END, DELIVERY_START, SENSITIVITY_CUTOFFS
from app.services.data_store import load_data
from app.services.selection import (
    build_scored,
    cutoff_for_targets,
    expected_hours,
    hourly_actuals,
    parse_cutoff,
    select_forecasts,
)


def ts(value: str) -> pd.Timestamp:
    return pd.Timestamp(value, tz="UTC")


def forecasts(rows: list[tuple[str, str, float]]) -> pd.DataFrame:
    """rows: (start_time, publish_time, generation_mw)."""
    return pd.DataFrame(
        {
            "start_time": pd.to_datetime([r[0] for r in rows], utc=True),
            "publish_time": pd.to_datetime([r[1] for r in rows], utc=True),
            "generation_mw": [r[2] for r in rows],
        }
    )


def actuals(rows: list[tuple[str, float]]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "start_time": pd.to_datetime([r[0] for r in rows], utc=True),
            "generation_mw": [r[1] for r in rows],
        }
    )


# --- cutoff parsing -------------------------------------------------------------------------


def test_parse_cutoff_valid() -> None:
    assert parse_cutoff("09:00") == time(9, 0)
    assert parse_cutoff("23:59") == time(23, 59)


@pytest.mark.parametrize("value", ["9:00", "24:00", "09:60", "abc", "", "09:00:00"])
def test_parse_cutoff_rejects_bad_input(value: str) -> None:
    with pytest.raises(ValueError):
        parse_cutoff(value)


# --- picking the forecast -------------------------------------------------------------------

TARGET = "2026-01-02T12:00:00Z"  # delivery day 2 Jan, so the 09:00 cutoff is 1 Jan 09:00 (GMT = UTC)


def test_picks_latest_forecast_at_or_before_cutoff() -> None:
    f = forecasts(
        [
            (TARGET, "2026-01-01T07:30:00Z", 100),
            (TARGET, "2026-01-01T09:00:00Z", 200),  # exactly at the cutoff: allowed
            (TARGET, "2026-01-01T09:30:00Z", 300),  # after the cutoff: never
        ]
    )
    chosen = select_forecasts(f, time(9, 0))
    assert chosen["forecast_mw"].tolist() == [200]
    assert chosen["horizon_h"].tolist() == [27.0]


def test_leakage_forecast_after_cutoff_is_never_used() -> None:
    f = forecasts(
        [(TARGET, "2026-01-01T09:01:00Z", 999), (TARGET, "2026-01-02T11:00:00Z", 999)]
    )
    assert select_forecasts(f, time(9, 0)).empty


def test_leakage_on_real_data_for_every_cutoff() -> None:
    store = load_data()
    for value in [*SENSITIVITY_CUTOFFS, "00:00", "23:59"]:
        cutoff = parse_cutoff(value)
        chosen = select_forecasts(store.forecasts, cutoff)
        deadline = cutoff_for_targets(chosen["start_time"], cutoff)
        assert (chosen["publish_time"] <= deadline).all(), value


def test_order_of_rows_does_not_matter() -> None:
    f = forecasts(
        [(TARGET, "2026-01-01T07:30:00Z", 100), (TARGET, "2026-01-01T04:30:00Z", 50)]
    )
    assert select_forecasts(f, time(9, 0))["forecast_mw"].tolist() == [100]


def test_late_batch_at_1225_is_used_only_after_it_exists() -> None:
    # On 15 Jan the 11:30 batch was replaced by one at 12:25.
    target = "2026-01-16T12:00:00Z"
    f = forecasts(
        [(target, "2026-01-15T09:30:00Z", 1), (target, "2026-01-15T12:25:00Z", 2)]
    )
    assert select_forecasts(f, time(12, 0))["forecast_mw"].tolist() == [1]
    assert select_forecasts(f, time(12, 25))["forecast_mw"].tolist() == [2]


def test_late_batch_on_real_data() -> None:
    store = load_data()
    scored, _ = build_scored(
        store.actuals,
        store.forecasts,
        time(13, 0),
        date(2026, 1, 16),
        date(2026, 1, 16),
    )
    assert (scored["publish_time"] == ts("2026-01-15T12:25:00Z")).all()


# --- UK time and daylight saving -------------------------------------------------------------


def test_cutoff_is_uk_time_in_summer() -> None:
    # In July the UK is on BST (UTC+1): 09:00 UK on 1 July is 08:00 UTC.
    deadline = cutoff_for_targets(pd.Series([ts("2026-07-02T12:00:00Z")]), time(9, 0))
    assert deadline.iloc[0] == ts("2026-07-01T08:00:00Z")


def test_delivery_day_uses_uk_date() -> None:
    # 23:30 UTC on 1 July is 00:30 on 2 July in the UK, so its decision is on 1 July.
    deadline = cutoff_for_targets(pd.Series([ts("2026-07-01T23:30:00Z")]), time(9, 0))
    assert deadline.iloc[0] == ts("2026-07-01T08:00:00Z")


def test_expected_hours_handle_clock_changes() -> None:
    assert len(expected_hours(date(2026, 1, 2), date(2026, 1, 2))) == 24
    assert (
        len(expected_hours(date(2026, 3, 29), date(2026, 3, 29))) == 23
    )  # clocks go forward
    assert (
        len(expected_hours(date(2026, 10, 25), date(2026, 10, 25))) == 25
    )  # clocks go back
    assert expected_hours(date(2026, 7, 2), date(2026, 7, 2))[0] == ts(
        "2026-07-01T23:00:00Z"
    )


# --- aligning half-hours with hours (option B) ------------------------------------------------


def test_hourly_actuals_average_both_half_hours() -> None:
    a = actuals([("2026-01-02T12:00:00Z", 100), ("2026-01-02T12:30:00Z", 200)])
    result = hourly_actuals(a)
    assert result["start_time"].tolist() == [ts("2026-01-02T12:00:00Z")]
    assert result["actual_mw"].tolist() == [150]


def test_hour_with_one_half_missing_is_dropped_not_guessed() -> None:
    a = actuals([("2026-01-02T12:00:00Z", 100)])
    assert hourly_actuals(a).empty


# --- joining and coverage --------------------------------------------------------------------


def test_build_scored_error_sign_and_coverage() -> None:
    day = date(2026, 1, 2)
    f = forecasts(
        [
            (TARGET, "2026-01-01T07:30:00Z", 1000),
            ("2026-01-02T13:00:00Z", "2026-01-01T07:30:00Z", 500),
        ]
    )
    a = actuals(
        [
            ("2026-01-02T12:00:00Z", 700),
            ("2026-01-02T12:30:00Z", 900),
            ("2026-01-02T14:00:00Z", 1),  # actual but no forecast for 14:00
            ("2026-01-02T14:30:00Z", 1),
        ]
    )
    scored, coverage = build_scored(a, f, time(9, 0), day, day)

    assert len(scored) == 1
    row = scored.iloc[0]
    assert row["actual_mw"] == 800
    assert (
        row["error_mw"] == 200
    )  # forecast 1000 - actual 800: positive = over-forecast
    assert row["abs_error_mw"] == 200
    assert coverage.expected == 24
    assert coverage.scored == 1
    assert coverage.skipped == 23
    assert coverage.missing_forecast == 22  # every hour except 12:00 and 13:00
    assert coverage.missing_actual == 22  # every hour except 12:00 and 14:00


def test_build_scored_with_no_data() -> None:
    empty_f = forecasts([])
    empty_a = actuals([])
    scored, coverage = build_scored(
        empty_a, empty_f, time(9, 0), date(2026, 1, 2), date(2026, 1, 3)
    )
    assert scored.empty
    assert coverage.expected == 48
    assert coverage.scored == 0


def test_full_window_on_real_data_is_fully_covered() -> None:
    store = load_data()
    _, coverage = build_scored(
        store.actuals, store.forecasts, time(9, 0), DELIVERY_START, DELIVERY_END
    )
    assert coverage.expected == 744
    assert coverage.scored == 744
