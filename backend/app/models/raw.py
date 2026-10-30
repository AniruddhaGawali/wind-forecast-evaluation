from datetime import datetime

from pydantic import BaseModel, Field


class ActualPoint(BaseModel):
    start_time: datetime = Field(description="Start of the half-hour slot, UTC")
    generation_mw: float


class ForecastPoint(BaseModel):
    start_time: datetime = Field(description="Target hour being forecast, UTC")
    publish_time: datetime = Field(description="When the forecast was made, UTC")
    generation_mw: float


class RawResponse(BaseModel):
    start: str
    end: str
    actuals: list[ActualPoint]
    forecasts: list[ForecastPoint]
