// Response shapes of the backend. Keep in sync with backend/app/models/.

export interface Coverage {
  expected: number;
  scored: number;
  skipped: number;
  missing_forecast: number;
  missing_actual: number;
}

export interface SeriesPoint {
  time: string; // target hour, ISO 8601 UTC
  actual_mw: number;
  forecast_mw: number;
  error_mw: number; // forecast - actual; positive = over-forecast
  horizon_h: number;
  publish_time: string;
}

export interface SeriesResponse {
  cutoff: string;
  start: string;
  end: string;
  coverage: Coverage;
  points: SeriesPoint[];
}

export interface Summary {
  n: number;
  mae: number | null;
  rmse: number | null;
  bias: number | null;
  p50: number | null;
  p90: number | null;
  p95: number | null;
  wape_pct: number | null;
}

export interface HourRow extends Summary {
  hour: number;
}
export interface DayRow extends Summary {
  day: string;
}
export interface HorizonRow extends Summary {
  horizon: string;
}
export interface LevelRow extends Summary {
  level: string;
}

export interface HistogramBin {
  lo: number;
  hi: number;
  count: number;
}

export interface MetricsResponse {
  cutoff: string;
  start: string;
  end: string;
  coverage: Coverage;
  summary: Summary;
  by_hour_of_day: HourRow[];
  by_day: DayRow[];
  by_horizon: HorizonRow[];
  by_generation_level: LevelRow[];
  error_histogram: HistogramBin[];
  recommendation: { buffer_mw: number | null; text: string };
}

/** What every analysis request needs. */
export interface AnalysisParams {
  start: string; // YYYY-MM-DD
  end: string;
  cutoff: string; // HH:MM, UK time on the day before delivery
}
