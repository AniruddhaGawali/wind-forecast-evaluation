import type { AnalysisParams, MetricsResponse, SensitivityResponse, SeriesResponse } from "./types";

// Where the API lives. Unset in a production build means the same origin: on Vercel, /api/* on the
// dashboard's own domain is routed to the backend service. `next dev` defaults to the local backend.
const BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  (process.env.NODE_ENV === "development" ? "http://127.0.0.1:8000" : "");
/** Give up on a request after this long so the user gets an error and a retry button, not a spinner forever. */
const TIMEOUT_MS = 20_000;

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

async function get<T>(path: string, params: Record<string, string> | URLSearchParams): Promise<T> {
  const url = `${BASE_URL}${path}?${new URLSearchParams(params)}`;
  let response: Response;
  try {
    response = await fetch(url, { signal: AbortSignal.timeout(TIMEOUT_MS) });
  } catch (error) {
    if (error instanceof DOMException && error.name === "TimeoutError") {
      throw new ApiError("The server took too long to answer.", 0);
    }
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

/** Metrics for several cutoffs over the same dates. Omit `cutoffs` for the backend default set. */
export function fetchSensitivity(
  params: Omit<AnalysisParams, "cutoff"> & { cutoffs?: string[] },
): Promise<SensitivityResponse> {
  const query = new URLSearchParams({ start: params.start, end: params.end });
  for (const cutoff of params.cutoffs ?? []) query.append("cutoffs", cutoff);
  return get<SensitivityResponse>("/api/v1/sensitivity", query);
}
