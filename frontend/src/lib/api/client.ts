import type { AnalysisParams, MetricsResponse, SeriesResponse } from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

async function get<T>(path: string, params: Record<string, string>): Promise<T> {
  const url = `${BASE_URL}${path}?${new URLSearchParams(params)}`;
  let response: Response;
  try {
    response = await fetch(url);
  } catch {
    throw new ApiError("Cannot reach the server. Is the backend running?", 0);
  }
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(body?.detail ?? `Request failed (${response.status})`, response.status);
  }
  return response.json() as Promise<T>;
}

export function fetchSeries(params: AnalysisParams): Promise<SeriesResponse> {
  return get<SeriesResponse>("/api/v1/series", { ...params });
}

export function fetchMetrics(params: AnalysisParams): Promise<MetricsResponse> {
  return get<MetricsResponse>("/api/v1/metrics", { ...params });
}
