import { useQuery } from "@tanstack/react-query";

import { fetchRaw } from "@/lib/api/client";

export function useRawData(start: string, end: string) {
  return useQuery({
    queryKey: ["raw", start, end],
    queryFn: () => fetchRaw(start, end),
    enabled: Boolean(start && end && start <= end),
  });
}
