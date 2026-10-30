from dataclasses import asdict
from datetime import time
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.models.analysis import (
    Coverage,
    MetricsResponse,
    Recommendation,
    SeriesResponse,
)
from app.routes.params import DateRange, cutoff_param, date_range
from app.services import metrics
from app.services.selection import Coverage as CoverageCounts
from app.services.selection import build_scored

router = APIRouter(prefix="/api/v1", tags=["analysis"])


def _coverage(c: CoverageCounts) -> Coverage:
    return Coverage(**asdict(c), skipped=c.skipped)


@router.get("/series", response_model=SeriesResponse)
def series(
    request: Request,
    dates: Annotated[DateRange, Depends(date_range)],
    cutoff: Annotated[time, Depends(cutoff_param)],
) -> SeriesResponse:
    """Per-hour actual, chosen forecast, error and horizon, for the main chart and drill-down."""
    store = request.app.state.data
    scored, coverage = build_scored(
        store.actuals, store.forecasts, cutoff, dates.start, dates.end
    )
    points = scored.rename(columns={"start_time": "time"})
    return SeriesResponse(
        cutoff=cutoff.strftime("%H:%M"),
        start=dates.start.isoformat(),
        end=dates.end.isoformat(),
        coverage=_coverage(coverage),
        points=points.to_dict("records"),  # type: ignore[arg-type]
    )


@router.get("/metrics", response_model=MetricsResponse)
def get_metrics(
    request: Request,
    dates: Annotated[DateRange, Depends(date_range)],
    cutoff: Annotated[time, Depends(cutoff_param)],
) -> MetricsResponse:
    """Summary metrics, breakdowns, error histogram and the buffer recommendation."""
    store = request.app.state.data
    scored, coverage = build_scored(
        store.actuals, store.forecasts, cutoff, dates.start, dates.end
    )
    summary = metrics.summarise(scored)
    return MetricsResponse(
        cutoff=cutoff.strftime("%H:%M"),
        start=dates.start.isoformat(),
        end=dates.end.isoformat(),
        coverage=_coverage(coverage),
        summary=summary.as_dict(),  # type: ignore[arg-type]
        by_hour_of_day=metrics.by_hour_of_day(scored),  # type: ignore[arg-type]
        by_day=metrics.by_day(scored),  # type: ignore[arg-type]
        by_horizon=metrics.by_horizon(scored),  # type: ignore[arg-type]
        by_generation_level=metrics.by_generation_level(scored),  # type: ignore[arg-type]
        error_histogram=metrics.error_histogram(scored),  # type: ignore[arg-type]
        recommendation=Recommendation(
            buffer_mw=metrics.buffer_mw(summary.p90),
            text=metrics.recommendation_text(summary.p90),
        ),
    )
