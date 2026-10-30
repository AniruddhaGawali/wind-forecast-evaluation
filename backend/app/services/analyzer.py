"""Runs the analysis on the loaded data and remembers results, so repeated requests are instant."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, time
from functools import lru_cache

import pandas as pd

from app.config import SCORED_CACHE_SIZE
from app.services import metrics
from app.services.data_store import DataStore
from app.services.selection import Coverage, build_scored


@dataclass(frozen=True)
class SensitivityResult:
    cutoff: time
    coverage: Coverage
    summary: metrics.Summary


class Analyzer:
    """Wraps `build_scored` with an in-memory cache keyed by (cutoff, start, end).

    The data never changes while the app runs, so a cached result never goes stale.
    Callers must treat the returned DataFrame as read-only: it is shared between requests.
    """

    def __init__(self, store: DataStore, cache_size: int = SCORED_CACHE_SIZE) -> None:
        self.store = store
        self.scored = lru_cache(maxsize=cache_size)(self._build)

    def _build(
        self, cutoff: time, start: date, end: date
    ) -> tuple[pd.DataFrame, Coverage]:
        return build_scored(
            self.store.actuals, self.store.forecasts, cutoff, start, end
        )

    def sensitivity(
        self, cutoffs: Iterable[time], start: date, end: date
    ) -> list[SensitivityResult]:
        """The same summary metrics for each cutoff, over the same delivery hours."""
        results = []
        for cutoff in cutoffs:
            scored, coverage = self.scored(cutoff, start, end)
            results.append(
                SensitivityResult(cutoff, coverage, metrics.summarise(scored))
            )
        return results
