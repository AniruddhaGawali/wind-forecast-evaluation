"use client";

import { useMemo } from "react";

import type { SensitivityRow } from "@/lib/api/types";

import { COLORS, mwTooltip } from "./colors";
import { EChart, type EChartsOption } from "./echart";

/** How the error changes with the decision time. The current cutoff is highlighted; click a bar to switch to it. */
export function SensitivityChart({
  rows,
  current,
  onSelect,
}: {
  rows: SensitivityRow[];
  current: string;
  onSelect?: (cutoff: string) => void;
}) {
  const option = useMemo<EChartsOption>(
    () => ({
      animation: false,
      color: [COLORS.error, COLORS.forecast],
      grid: { left: 56, right: 16, top: 40, bottom: 48 },
      legend: { top: 0 },
      tooltip: { trigger: "axis", valueFormatter: mwTooltip },
      xAxis: {
        type: "category",
        data: rows.map((r) => r.cutoff),
        name: "Decision time (UK, day before)",
        nameLocation: "middle",
        nameGap: 30,
        axisLabel: {
          interval: 0,
          hideOverlap: true,
          formatter: (v: string) => (v === current ? `{b|${v}}` : v),
          rich: { b: { fontWeight: "bold" } },
        },
      },
      yAxis: { type: "value", name: "MW", nameLocation: "middle", nameGap: 40 },
      series: [
        {
          name: "Typical miss (MAE)",
          type: "bar",
          // Fade the cutoffs that are not selected so the current one stands out.
          data: rows.map((r) => ({
            value: r.mae,
            itemStyle: { opacity: r.cutoff === current ? 1 : 0.45 },
          })),
        },
        {
          name: "Buffer for 90% (P90)",
          type: "line",
          symbolSize: 7,
          data: rows.map((r) => r.buffer_mw),
        },
      ],
    }),
    [rows, current],
  );
  return (
    <EChart
      option={option}
      label="Typical miss and P90 buffer for each decision time"
      className="h-64 w-full"
      onClickX={onSelect && ((x) => onSelect(String(x)))}
    />
  );
}
