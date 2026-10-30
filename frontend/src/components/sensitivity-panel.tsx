"use client";

import { SensitivityChart } from "@/components/charts/sensitivity-chart";
import { QueryState } from "@/components/query-state";
import { useSensitivity } from "@/hooks/use-analysis";
import type { AnalysisParams } from "@/lib/api/types";
import { sensitivityCutoffs } from "@/lib/dates";

interface Props {
  params: AnalysisParams;
  onCutoffChange: (cutoff: string) => void;
}

/** Error for several decision times over the same dates, from the backend sensitivity endpoint. */
export function SensitivityPanel({ params, onCutoffChange }: Props) {
  const sensitivity = useSensitivity({
    start: params.start,
    end: params.end,
    cutoffs: sensitivityCutoffs(params.cutoff),
  });
  return (
    <QueryState
      isPending={sensitivity.isPending}
      error={sensitivity.error}
      onRetry={() => sensitivity.refetch()}
      isEmpty={sensitivity.data?.results.every((r) => r.n === 0)}
      skeletonClassName="h-64 w-full"
    >
      {sensitivity.data && (
        <SensitivityChart
          rows={sensitivity.data.results}
          current={params.cutoff}
          onSelect={onCutoffChange}
        />
      )}
    </QueryState>
  );
}
