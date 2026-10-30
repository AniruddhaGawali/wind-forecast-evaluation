from datetime import date, timedelta

import pandas as pd

from app.services.data_store import DataStore


def select_raw(
    store: DataStore, start: date, end: date, all_forecasts: bool
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Actuals and forecasts whose target time is on a UTC day in [start, end] (inclusive).

    By default only the latest forecast per target hour is returned, and only forecasts
    published at or before their target time. Pass all_forecasts to get every version.
    """
    lo = pd.Timestamp(start, tz="UTC")
    hi = pd.Timestamp(end + timedelta(days=1), tz="UTC")

    actuals = store.actuals[
        store.actuals["start_time"].between(lo, hi, inclusive="left")
    ]
    forecasts = store.forecasts[
        store.forecasts["start_time"].between(lo, hi, inclusive="left")
    ]
    if not all_forecasts:
        forecasts = forecasts[forecasts["publish_time"] <= forecasts["start_time"]]
        forecasts = (
            forecasts.sort_values("publish_time")
            .groupby("start_time", as_index=False)
            .last()
        )
    return actuals, forecasts.sort_values(["start_time", "publish_time"])
