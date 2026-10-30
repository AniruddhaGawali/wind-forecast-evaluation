// Response shapes of the backend. Keep in sync with backend/app/models/.

export interface ActualPoint {
  start_time: string; // ISO 8601, UTC
  generation_mw: number;
}

export interface ForecastPoint {
  start_time: string; // target hour, UTC
  publish_time: string; // when the forecast was made, UTC
  generation_mw: number;
}

export interface RawResponse {
  start: string;
  end: string;
  actuals: ActualPoint[];
  forecasts: ForecastPoint[];
}
