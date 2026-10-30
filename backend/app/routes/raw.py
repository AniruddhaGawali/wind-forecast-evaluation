from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from app.models.raw import RawResponse
from app.routes.params import DateRange, date_range
from app.services.raw import select_raw

router = APIRouter(prefix="/api/v1", tags=["raw"])


@router.get("/raw", response_model=RawResponse)
def raw(
    request: Request,
    dates: Annotated[DateRange, Depends(date_range)],
    all_forecasts: Annotated[
        bool,
        Query(
            description="Return every forecast version, not just the latest per hour"
        ),
    ] = False,
) -> RawResponse:
    """Raw actual wind and forecasts for a date range. A sanity view, not the final analysis."""
    actuals, forecasts = select_raw(
        request.app.state.data, dates.start, dates.end, all_forecasts
    )
    return RawResponse(
        start=dates.start.isoformat(),
        end=dates.end.isoformat(),
        actuals=actuals.to_dict("records"),  # type: ignore[arg-type]
        forecasts=forecasts.to_dict("records"),  # type: ignore[arg-type]
    )
