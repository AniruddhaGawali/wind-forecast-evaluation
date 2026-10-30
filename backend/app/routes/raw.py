from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.models.errors import ERROR_RESPONSES
from app.models.raw import RawResponse
from app.routes.params import DateRange, date_range, get_analyzer
from app.services.analyzer import Analyzer
from app.services.raw import select_raw

router = APIRouter(prefix="/api/v1", tags=["raw"], responses=ERROR_RESPONSES)


@router.get("/raw", response_model=RawResponse, summary="Raw actuals and forecasts")
def raw(
    analyzer: Annotated[Analyzer, Depends(get_analyzer)],
    dates: Annotated[DateRange, Depends(date_range)],
    all_forecasts: Annotated[
        bool,
        Query(
            description="Return every forecast version, not just the latest per hour"
        ),
    ] = False,
) -> RawResponse:
    """Raw actual wind (half-hourly) and forecasts (hourly) for a date range.

    A sanity view of the stored data, not the analysis: no cutoff is applied.
    """
    actuals, forecasts = select_raw(
        analyzer.store, dates.start, dates.end, all_forecasts
    )
    return RawResponse(
        start=dates.start.isoformat(),
        end=dates.end.isoformat(),
        actuals=actuals.to_dict("records"),  # type: ignore[arg-type]
        forecasts=forecasts.to_dict("records"),  # type: ignore[arg-type]
    )
