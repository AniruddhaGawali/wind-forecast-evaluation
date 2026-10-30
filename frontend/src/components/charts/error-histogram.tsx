"use client";

import { useMemo } from "react";

import type { HistogramBin } from "@/lib/api/types";

import { COLORS } from "./colors";
import { EChart, type EChartsOption } from "./echart";

const label = (b: HistogramBin) => `${(b.lo / 1000).toFixed(1)} to ${(b.hi / 1000).toFixed(1)} GW`;

/** How often each size of error happened. Bins are computed by the backend. */
export function ErrorHistogram({ bins }: { bins: HistogramBin[] }) {
  const option = useMemo<EChartsOption>(
    () => ({
      animation: false,
      color: [COLORS.error],
      grid: { left: 56, right: 16, top: 16, bottom: 56 },
      tooltip: { trigger: "axis" },
      xAxis: {
        type: "category",
        data: bins.map(label),
        name: "Error (forecast - actual)",
        nameLocation: "middle",
        nameGap: 36,
        axisLabel: { formatter: (_: string, i: number) => `${bins[i].lo / 1000}` },
      },
      yAxis: { type: "value", name: "Hours", nameLocation: "middle", nameGap: 36 },
      series: [
        { name: "Hours", type: "bar", barCategoryGap: "4%", data: bins.map((b) => b.count) },
      ],
    }),
    [bins],
  );
  return <EChart option={option} className="h-64 w-full" />;
}
