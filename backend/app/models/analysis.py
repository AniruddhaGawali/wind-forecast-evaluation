from datetime import datetime

from pydantic import BaseModel, Field


class SeriesPoint(BaseModel):
    time: datetime = Field(description="Target hour, UTC")
    actual_mw: float = Field(
        description="Average of the two half-hour actuals in this hour"
    )
    forecast_mw: float = Field(description="Forecast chosen at the cutoff")
    error_mw: float = Field(
        description="forecast - actual; positive means over-forecast"
    )
    horizon_h: float = Field(
        description="Hours between the forecast's publish time and the target hour"
    )
    publish_time: datetime = Field(
        description="When the chosen forecast was published, UTC"
    )


class Coverage(BaseModel):
    expected: int = Field(description="Hours in the date range")
    scored: int = Field(description="Hours with both a forecast and an actual")
    skipped: int = Field(description="expected - scored")
    missing_forecast: int = Field(
        description="Hours with no forecast published before the cutoff"
    )
    missing_actual: int = Field(description="Hours without both half-hour actuals")


class SeriesResponse(BaseModel):
    cutoff: str = Field(description="Decision time on D-1, UK time, HH:MM")
    start: str = Field(description="First delivery date, inclusive")
    end: str = Field(description="Last delivery date, inclusive")
    coverage: Coverage
    points: list[SeriesPoint]


class Summary(BaseModel):
    n: int = Field(description="Hours scored")
    mae: float | None = Field(description="Mean absolute error, MW")
    rmse: float | None = Field(description="Root mean square error, MW")
    bias: float | None = Field(
        description="Mean signed error, MW; positive = forecasts too high"
    )
    p50: float | None = Field(description="Median absolute error, MW")
    p90: float | None = Field(description="90th percentile of absolute error, MW")
    p95: float | None = Field(description="95th percentile of absolute error, MW")
    wape_pct: float | None = Field(
        description="Sum of absolute errors / sum of actuals x 100"
    )


class HourRow(Summary):
    hour: int = Field(description="UTC hour of day, 0-23")


class DayRow(Summary):
    day: str = Field(description="UK delivery day, YYYY-MM-DD")


class HorizonRow(Summary):
    horizon: str = Field(description="Forecast age bucket, e.g. 24-36h")


class LevelRow(Summary):
    level: str = Field(description="Actual output bucket, e.g. 10-15 GW")


class HistogramBin(BaseModel):
    lo: float = Field(description="Lower edge of the error bin, MW (inclusive)")
    hi: float = Field(description="Upper edge, MW (exclusive)")
    count: int = Field(description="Hours whose error falls in this bin")


class Recommendation(BaseModel):
    buffer_mw: int | None = Field(
        description="P90 absolute error rounded up to a whole MW"
    )
    text: str = Field(description="The recommendation as one plain-English sentence")


class MetricsResponse(BaseModel):
    cutoff: str = Field(description="Decision time on D-1, UK time, HH:MM")
    start: str = Field(description="First delivery date, inclusive")
    end: str = Field(description="Last delivery date, inclusive")
    coverage: Coverage
    summary: Summary
    by_hour_of_day: list[HourRow]
    by_day: list[DayRow]
    by_horizon: list[HorizonRow]
    by_generation_level: list[LevelRow]
    error_histogram: list[HistogramBin]
    recommendation: Recommendation


class SensitivityRow(Summary):
    cutoff: str = Field(description="Decision time on D-1, UK time, HH:MM")
    coverage: Coverage
    buffer_mw: int | None = Field(
        description="P90 absolute error rounded up to a whole MW"
    )


class SensitivityResponse(BaseModel):
    start: str = Field(description="First delivery date, inclusive")
    end: str = Field(description="Last delivery date, inclusive")
    results: list[SensitivityRow] = Field(
        description="One row per cutoff, earliest first"
    )
