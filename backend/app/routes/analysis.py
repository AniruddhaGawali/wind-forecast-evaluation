from dataclasses import asdict
from datetime import time
from typing import Annotated

from fastapi import APIRouter, Depends

from app.models.analysis import (
    Coverage,
    MetricsResponse,
    Recommendation,
    SensitivityResponse,
    SensitivityRow,
    SeriesResponse,
)
from app.models.errors import ERROR_RESPONSES
from app.routes.params import (
    DateRange,
    cutoff_param,
    cutoffs_param,
    date_range,
    get_analyzer,
)
from app.services import metrics
from app.services.analyzer import Analyzer
from app.services.selection import Coverage as CoverageCounts

router = APIRouter(prefix="/api/v1", tags=["analysis"], responses=ERROR_RESPONSES)


def _coverage(c: CoverageCounts) -> Coverage:
    return Coverage(**asdict(c), skipped=c.skipped)


@router.get(
    "/series", response_model=SeriesResponse, summary="Hourly forecast vs actual"
)
def series(
    analyzer: Annotated[Analyzer, Depends(get_analyzer)],
    dates: Annotated[DateRange, Depends(date_range)],
    cutoff: Annotated[time, Depends(cutoff_param)],
) -> SeriesResponse:
    """Per-hour actual, chosen forecast, error and horizon, for the main chart and drill-down.

    For each target hour the chosen forecast is the latest one published at or before
    `cutoff` (UK time) on the day before delivery. Hours with no such forecast, or without
    both half-hour actuals, are left out and counted in `coverage`.
    """
    scored, coverage = analyzer.scored(cutoff, dates.start, dates.end)
    points = scored.rename(columns={"start_time": "time"})
    return SeriesResponse(
        cutoff=cutoff.strftime("%H:%M"),
        start=dates.start.isoformat(),
        end=dates.end.isoformat(),
        coverage=_coverage(coverage),
        points=points.to_dict("records"),  # type: ignore[arg-type]
    )


@router.get(
    "/metrics", response_model=MetricsResponse, summary="Error metrics for one cutoff"
)
def get_metrics(
    analyzer: Annotated[Analyzer, Depends(get_analyzer)],
    dates: Annotated[DateRange, Depends(date_range)],
    cutoff: Annotated[time, Depends(cutoff_param)],
) -> MetricsResponse:
    """Summary metrics, breakdowns, error histogram (500 MW bins) and the buffer recommendation.

    error = forecast - actual, so a positive bias means forecasts were too high.
    Percentiles are of the absolute error, nearest-rank method. The buffer is P90 rounded up.
    """
    scored, coverage = analyzer.scored(cutoff, dates.start, dates.end)
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


@router.get(
    "/sensitivity",
    response_model=SensitivityResponse,
    summary="Compare error metrics across cutoffs",
)
def sensitivity(
    analyzer: Annotated[Analyzer, Depends(get_analyzer)],
    dates: Annotated[DateRange, Depends(date_range)],
    cutoffs: Annotated[list[time], Depends(cutoffs_param)],
) -> SensitivityResponse:
    """The summary metrics and buffer for several cutoff times over the same delivery hours.

    Shows how much accuracy depends on when the decision is made: a later cutoff allows a
    fresher forecast. Example: `?start=2026-01-02&end=2026-02-01&cutoffs=06:00&cutoffs=12:00`.
    """
    results = analyzer.sensitivity(cutoffs, dates.start, dates.end)
    return SensitivityResponse(
        start=dates.start.isoformat(),
        end=dates.end.isoformat(),
        results=[
            SensitivityRow(
                cutoff=r.cutoff.strftime("%H:%M"),
                coverage=_coverage(r.coverage),
                buffer_mw=metrics.buffer_mw(r.summary.p90),
                **r.summary.as_dict(),  # type: ignore[arg-type]
            )
            for r in results
        ],
    )
