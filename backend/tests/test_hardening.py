import io
import json
import logging
import math
from collections.abc import Iterator
from datetime import time
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.logging_setup import JsonFormatter
from app.main import app
from app.routes.params import get_analyzer
from app.services.analyzer import Analyzer
from app.services.data_store import DataStore, load_data

FULL = {"start": "2026-01-02", "end": "2026-02-01"}
ONE_DAY = {"start": "2026-01-02", "end": "2026-01-02"}


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


def _empty_store() -> DataStore:
    utc = pd.DatetimeTZDtype("ns", "UTC")
    return DataStore(
        actuals=pd.DataFrame(
            {
                "start_time": pd.Series(dtype=utc),
                "generation_mw": pd.Series(dtype=float),
            }
        ),
        forecasts=pd.DataFrame(
            {
                "start_time": pd.Series(dtype=utc),
                "publish_time": pd.Series(dtype=utc),
                "generation_mw": pd.Series(dtype=float),
            }
        ),
    )


@pytest.fixture
def empty_client(client: TestClient) -> Iterator[TestClient]:
    """The same app, but every route sees a data store with no rows."""
    app.dependency_overrides[get_analyzer] = lambda: Analyzer(_empty_store())
    yield client
    app.dependency_overrides.clear()


# --- /api/v1/sensitivity ---


def test_sensitivity_default_cutoffs(client: TestClient) -> None:
    body = client.get("/api/v1/sensitivity", params=FULL).json()
    rows = body["results"]
    assert [r["cutoff"] for r in rows] == ["06:00", "09:00", "10:00", "12:00", "18:00"]
    assert all(r["coverage"]["scored"] == 744 for r in rows)
    assert all(r["buffer_mw"] == math.ceil(r["p90"]) for r in rows)


def test_sensitivity_row_matches_metrics(client: TestClient) -> None:
    rows = client.get("/api/v1/sensitivity", params=FULL).json()["results"]
    nine = next(r for r in rows if r["cutoff"] == "09:00")
    summary = client.get("/api/v1/metrics", params=FULL).json()["summary"]
    for key in ("n", "mae", "rmse", "bias", "p50", "p90", "p95", "wape_pct"):
        assert nine[key] == summary[key]


def test_sensitivity_custom_cutoffs_are_deduped_and_sorted(client: TestClient) -> None:
    params = {**ONE_DAY, "cutoffs": ["12:00", "06:00", "12:00"]}
    rows = client.get("/api/v1/sensitivity", params=params).json()["results"]
    assert [r["cutoff"] for r in rows] == ["06:00", "12:00"]


def test_sensitivity_later_cutoff_is_more_accurate(client: TestClient) -> None:
    params = {**FULL, "cutoffs": ["06:00", "18:00"]}
    early, late = client.get("/api/v1/sensitivity", params=params).json()["results"]
    assert late["mae"] < early["mae"]


@pytest.mark.parametrize(
    ("cutoffs", "message"),
    [
        (["06:00", "6am"], "HH:MM"),
        ([f"{h:02d}:00" for h in range(13)], "At most 12"),
    ],
)
def test_sensitivity_bad_cutoffs(
    client: TestClient, cutoffs: list[str], message: str
) -> None:
    r = client.get("/api/v1/sensitivity", params={**FULL, "cutoffs": cutoffs})
    assert r.status_code == 422
    assert message in r.json()["detail"]


def test_sensitivity_rejects_date_outside_window(client: TestClient) -> None:
    r = client.get(
        "/api/v1/sensitivity", params={"start": "2026-02-01", "end": "2026-02-02"}
    )
    assert r.status_code == 422
    assert "between" in r.json()["detail"]


# --- consistent error responses ---


@pytest.mark.parametrize(
    ("params", "field"),
    [
        ({"end": "2026-01-05"}, "start"),
        ({"start": "nope", "end": "2026-01-05"}, "start"),
        ({"start": "2026-01-02", "end": "2026-13-01"}, "end"),
    ],
)
def test_framework_validation_errors_are_one_string(
    client: TestClient, params: dict[str, str], field: str
) -> None:
    r = client.get("/api/v1/metrics", params=params)
    assert r.status_code == 422
    detail = r.json()["detail"]
    assert isinstance(detail, str)
    assert detail.startswith(f"{field}: ")


def test_unknown_path_is_404_with_detail(client: TestClient) -> None:
    r = client.get("/api/v1/nope")
    assert r.status_code == 404
    assert isinstance(r.json()["detail"], str)


def test_unexpected_error_is_500_with_detail() -> None:
    def broken() -> Analyzer:
        raise RuntimeError("boom")

    app.dependency_overrides[get_analyzer] = broken
    try:
        with TestClient(app, raise_server_exceptions=False) as c:
            r = c.get("/api/v1/metrics", params=ONE_DAY)
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 500
    assert r.json() == {"detail": "Internal server error."}  # no internals leaked


# --- empty result ---


def test_metrics_with_no_data(empty_client: TestClient) -> None:
    body = empty_client.get("/api/v1/metrics", params=ONE_DAY).json()
    assert body["coverage"] == {
        "expected": 24,
        "scored": 0,
        "skipped": 24,
        "missing_forecast": 24,
        "missing_actual": 24,
    }
    assert body["summary"]["n"] == 0
    assert body["summary"]["mae"] is None
    assert body["by_hour_of_day"] == []
    assert body["error_histogram"] == []
    assert body["recommendation"] == {
        "buffer_mw": None,
        "text": "Not enough data to recommend a buffer.",
    }


def test_series_and_sensitivity_with_no_data(empty_client: TestClient) -> None:
    assert empty_client.get("/api/v1/series", params=ONE_DAY).json()["points"] == []
    rows = empty_client.get("/api/v1/sensitivity", params=ONE_DAY).json()["results"]
    assert all(r["n"] == 0 and r["buffer_mw"] is None for r in rows)


# --- cache ---


def test_analyzer_caches_per_cutoff_and_range(client: TestClient) -> None:
    analyzer = Analyzer(load_data())
    first = analyzer.scored(
        time(9), pd.Timestamp("2026-01-02").date(), pd.Timestamp("2026-01-03").date()
    )
    again = analyzer.scored(
        time(9), pd.Timestamp("2026-01-02").date(), pd.Timestamp("2026-01-03").date()
    )
    other = analyzer.scored(
        time(12), pd.Timestamp("2026-01-02").date(), pd.Timestamp("2026-01-03").date()
    )
    assert again is first
    assert other is not first
    info = analyzer.scored.cache_info()
    assert (info.hits, info.misses) == (1, 2)


# --- start-up checks ---


def _write(path: Path, df: pd.DataFrame) -> Path:
    df.to_parquet(path)
    return path


def test_load_data_fails_on_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="--refresh"):
        load_data(tmp_path / "a.parquet", tmp_path / "f.parquet")


def test_load_data_fails_on_missing_columns(tmp_path: Path) -> None:
    store = _empty_store()
    actuals = _write(
        tmp_path / "a.parquet", pd.DataFrame({"start_time": [1], "x": [2]})
    )
    forecasts = _write(tmp_path / "f.parquet", store.forecasts)
    with pytest.raises(ValueError, match="missing columns"):
        load_data(actuals, forecasts)


def test_load_data_fails_on_empty_file(tmp_path: Path) -> None:
    store = _empty_store()
    actuals = _write(tmp_path / "a.parquet", store.actuals)
    forecasts = _write(tmp_path / "f.parquet", store.forecasts)
    with pytest.raises(ValueError, match="no rows"):
        load_data(actuals, forecasts)


# --- logging ---


def test_json_formatter_includes_fields_and_exception() -> None:
    try:
        raise ValueError("bad")
    except ValueError:
        import sys

        record = logging.LogRecord(
            "app", logging.ERROR, __file__, 1, "oops", None, sys.exc_info()
        )
    record.fields = {"path": "/x", "status": 500}
    line = json.loads(JsonFormatter().format(record))
    assert line["message"] == "oops"
    assert line["level"] == "ERROR"
    assert line["path"] == "/x"
    assert line["status"] == 500
    assert "ValueError: bad" in line["exception"]


def test_each_request_is_logged(client: TestClient) -> None:
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("app")
    logger.addHandler(handler)
    try:
        client.get("/api/v1/metrics", params={**ONE_DAY, "cutoff": "9am"})
    finally:
        logger.removeHandler(handler)
    line = json.loads(stream.getvalue().strip().splitlines()[-1])
    assert line["message"] == "request"
    assert line["path"] == "/api/v1/metrics"
    assert line["status"] == 422
    assert "cutoff=9am" in line["query"]
    assert line["duration_ms"] >= 0


# --- docs ---


def test_every_endpoint_is_documented(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    for path, ops in spec["paths"].items():
        for method, op in ops.items():
            assert op.get("summary"), f"{method} {path} has no summary"
            assert op.get("description"), f"{method} {path} has no description"
            for param in op.get("parameters", []):
                assert param.get("description"), f"{path} ?{param['name']} undocumented"
