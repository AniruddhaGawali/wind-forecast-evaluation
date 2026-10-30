from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:  # the context manager runs start-up (loads the data)
        yield c


def test_index_points_to_docs(client: TestClient) -> None:
    assert client.get("/").json()["docs"] == "/docs"


def test_health(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_raw_one_day_latest_forecast(client: TestClient) -> None:
    body = client.get(
        "/api/v1/raw", params={"start": "2026-01-02", "end": "2026-01-02"}
    ).json()
    assert len(body["actuals"]) == 48
    assert len(body["forecasts"]) == 24  # one per target hour
    assert all(f["publish_time"] <= f["start_time"] for f in body["forecasts"])


def test_raw_all_forecasts_returns_more(client: TestClient) -> None:
    params = {"start": "2026-01-02", "end": "2026-01-02", "all_forecasts": "true"}
    assert len(client.get("/api/v1/raw", params=params).json()["forecasts"]) > 24


def test_raw_rejects_date_outside_window(client: TestClient) -> None:
    r = client.get("/api/v1/raw", params={"start": "2025-12-01", "end": "2026-01-02"})
    assert r.status_code == 422


def test_raw_rejects_start_after_end(client: TestClient) -> None:
    r = client.get("/api/v1/raw", params={"start": "2026-01-10", "end": "2026-01-05"})
    assert r.status_code == 422


def test_raw_rejects_bad_date_format(client: TestClient) -> None:
    assert (
        client.get(
            "/api/v1/raw", params={"start": "nope", "end": "2026-01-05"}
        ).status_code
        == 422
    )


def test_cors_allows_frontend_origin(client: TestClient) -> None:
    r = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert r.headers["access-control-allow-origin"] == "http://localhost:3000"
