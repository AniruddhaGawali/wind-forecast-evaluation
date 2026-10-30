import logging
import time
from collections.abc import Iterator
from datetime import date, datetime, timedelta
from typing import Any

import httpx

from app.config import CHUNK_DAYS, ELEXON_BASE_URL, MAX_RETRIES, REQUEST_TIMEOUT_S

logger = logging.getLogger(__name__)

Row = dict[str, Any]


def _get_json(client: httpx.Client, path: str, params: dict[str, str]) -> list[Row]:
    """GET a stream endpoint, retrying transient failures with exponential backoff."""
    for attempt in range(1, MAX_RETRIES + 1):
        started = time.perf_counter()
        try:
            response = client.get(path, params=params)
            response.raise_for_status()
        except (httpx.TransportError, httpx.HTTPStatusError) as exc:
            if attempt == MAX_RETRIES:
                raise
            delay = 2**attempt
            logger.warning(
                "GET %s failed (%s); retry %d in %ds", path, exc, attempt, delay
            )
            time.sleep(delay)
            continue
        rows: list[Row] = response.json()
        logger.info(
            "GET %s %s -> %d rows in %.1fs",
            path,
            params,
            len(rows),
            time.perf_counter() - started,
        )
        return rows
    raise AssertionError("unreachable")


def _date_chunks(start: date, end: date) -> Iterator[tuple[date, date]]:
    """Split [start, end] (inclusive) into consecutive inclusive chunks of CHUNK_DAYS."""
    current = start
    while current <= end:
        chunk_end = min(current + timedelta(days=CHUNK_DAYS - 1), end)
        yield current, chunk_end
        current = chunk_end + timedelta(days=1)


def _datetime_chunks(
    start: datetime, end: datetime
) -> Iterator[tuple[datetime, datetime]]:
    current = start
    step = timedelta(days=CHUNK_DAYS)
    while current < end:
        chunk_end = min(current + step, end)
        yield current, chunk_end
        current = chunk_end


def _iso(value: datetime) -> str:
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def make_client() -> httpx.Client:
    return httpx.Client(base_url=ELEXON_BASE_URL, timeout=REQUEST_TIMEOUT_S)


def fetch_actuals(client: httpx.Client, start: date, end: date) -> list[Row]:
    """FUELHH wind generation, fetched by settlement date. Dates are inclusive."""
    rows: list[Row] = []
    for chunk_start, chunk_end in _date_chunks(start, end):
        rows += _get_json(
            client,
            "/datasets/FUELHH/stream",
            {
                "settlementDateFrom": chunk_start.isoformat(),
                "settlementDateTo": chunk_end.isoformat(),
                "fuelType": "WIND",
            },
        )
    return rows


def fetch_forecasts(client: httpx.Client, start: datetime, end: datetime) -> list[Row]:
    """WINDFOR forecasts, fetched by publish time."""
    rows: list[Row] = []
    for chunk_start, chunk_end in _datetime_chunks(start, end):
        rows += _get_json(
            client,
            "/datasets/WINDFOR/stream",
            {
                "publishDateTimeFrom": _iso(chunk_start),
                "publishDateTimeTo": _iso(chunk_end),
            },
        )
    return rows
