"""Query parameters shared by several routes, validated once here."""

from dataclasses import dataclass
from datetime import date, time
from typing import Annotated

from fastapi import HTTPException, Query

from app.config import DEFAULT_CUTOFF, DELIVERY_END, DELIVERY_START
from app.services.selection import parse_cutoff


@dataclass(frozen=True)
class DateRange:
    start: date
    end: date


def date_range(
    start: Annotated[
        date,
        Query(description="First delivery date, inclusive", examples=["2026-01-02"]),
    ],
    end: Annotated[
        date,
        Query(description="Last delivery date, inclusive", examples=["2026-02-01"]),
    ],
) -> DateRange:
    for value in (start, end):
        if not DELIVERY_START <= value <= DELIVERY_END:
            raise HTTPException(
                422,
                f"Dates must be between {DELIVERY_START} and {DELIVERY_END}, got {value}.",
            )
    if start > end:
        raise HTTPException(422, f"start ({start}) must be on or before end ({end}).")
    return DateRange(start, end)


def cutoff_param(
    cutoff: Annotated[
        str,
        Query(
            description="Decision time on the day before delivery, UK time, HH:MM",
            examples=[DEFAULT_CUTOFF],
        ),
    ] = DEFAULT_CUTOFF,
) -> time:
    try:
        return parse_cutoff(cutoff)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
