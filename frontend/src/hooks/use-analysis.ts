import { keepPreviousData, useQuery } from "@tanstack/react-query";

import { fetchMetrics, fetchSeries } from "@/lib/api/client";
import type { AnalysisParams } from "@/lib/api/types";

// keepPreviousData: while a new cutoff loads, keep showing the old numbers instead of flashing a skeleton.

export function useMetrics(params: AnalysisParams) {
  return useQuery({
    queryKey: ["metrics", params],
    queryFn: () => fetchMetrics(params),
    placeholderData: keepPreviousData,
  });
}

export function useSeries(params: AnalysisParams) {
  return useQuery({
    queryKey: ["series", params],
    queryFn: () => fetchSeries(params),
    placeholderData: keepPreviousData,
  });
}
