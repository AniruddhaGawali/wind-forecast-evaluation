from collections.abc import Iterator
from datetime import UTC, datetime, time, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app

FULL = {"start": "2026-01-02", "end": "2026-02-01"}


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


def test_series_one_day(client: TestClient) -> None:
    body = client.get(
        "/api/v1/series", params={"start": "2026-01-02", "end": "2026-01-02"}
    ).json()
    assert body["cutoff"] == "09:00"  # default
    assert body["coverage"] == {
        "expected": 24,
        "scored": 24,
        "skipped": 0,
        "missing_forecast": 0,
        "missing_actual": 0,
    }
    noon = next(p for p in body["points"] if p["time"].startswith("2026-01-02T12:00"))
    assert noon["forecast_mw"] == 17541
    assert noon["actual_mw"] == 14757.5
    assert noon["error_mw"] == 2783.5
    assert noon["horizon_h"] == 28.5


def test_series_never_uses_forecast_after_cutoff(client: TestClient) -> None:
    body = client.get("/api/v1/series", params={**FULL, "cutoff": "10:00"}).json()
    assert len(body["points"]) == 744
    for p in body["points"]:
        target = datetime.fromisoformat(p["time"])
        # January: UK time = UTC, so the deadline is 10:00 UTC on the day before delivery
        deadline = datetime.combine(
            target.date() - timedelta(days=1), time(10, 0), tzinfo=UTC
        )
        assert datetime.fromisoformat(p["publish_time"]) <= deadline


def test_metrics_full_window_default_cutoff(client: TestClient) -> None:
    body = client.get("/api/v1/metrics", params=FULL).json()
    assert body["coverage"]["scored"] == 744
    s = body["summary"]
    assert round(s["mae"]) == 2039
    assert s["p90"] == 4098.5
    assert body["recommendation"]["buffer_mw"] == 4099  # rounded up
    assert "4,099 MW" in body["recommendation"]["text"]
    assert len(body["by_hour_of_day"]) == 24
    assert len(body["by_day"]) == 31
    assert sum(b["count"] for b in body["error_histogram"]) == 744


def test_metrics_changes_with_cutoff(client: TestClient) -> None:
    early = client.get("/api/v1/metrics", params={**FULL, "cutoff": "09:00"}).json()[
        "summary"
    ]
    late = client.get("/api/v1/metrics", params={**FULL, "cutoff": "12:00"}).json()[
        "summary"
    ]
    assert late["mae"] < early["mae"]


@pytest.mark.parametrize("path", ["/api/v1/series", "/api/v1/metrics"])
@pytest.mark.parametrize(
    ("params", "message"),
    [
        ({**FULL, "cutoff": "9am"}, "HH:MM"),
        ({**FULL, "cutoff": "25:00"}, "HH:MM"),
        ({"start": "2026-01-01", "end": "2026-01-05"}, "between"),
        ({"start": "2026-01-10", "end": "2026-01-05"}, "on or before"),
    ],
)
def test_bad_input_returns_clear_422(
    client: TestClient, path: str, params: dict[str, str], message: str
) -> None:
    r = client.get(path, params=params)
    assert r.status_code == 422
    assert message in r.json()["detail"]


def test_missing_dates_is_422(client: TestClient) -> None:
    assert client.get("/api/v1/metrics").status_code == 422
