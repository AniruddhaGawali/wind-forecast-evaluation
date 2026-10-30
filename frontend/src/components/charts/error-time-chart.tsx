"use client";

import { useMemo } from "react";

import type { SeriesPoint } from "@/lib/api/types";

import { COLORS } from "./colors";
import { EChart, type EChartsOption } from "./echart";

/** Signed error per hour. Above zero = forecast too high. */
export function ErrorTimeChart({ points }: { points: SeriesPoint[] }) {
  const option = useMemo<EChartsOption>(
    () => ({
      animation: false,
      color: [COLORS.error],
      grid: { left: 64, right: 24, top: 16, bottom: 40 },
      tooltip: {
        trigger: "axis",
        valueFormatter: (v: number) => `${Math.round(v).toLocaleString("en-GB")} MW`,
      },
      xAxis: { type: "time" },
      yAxis: { type: "value", name: "Error (MW)", nameLocation: "middle", nameGap: 48 },
      dataZoom: [{ type: "inside" }],
      series: [
        {
          name: "Forecast - actual",
          type: "bar",
          barMaxWidth: 6,
          data: points.map((p) => [p.time, p.error_mw]),
          markLine: {
            silent: true,
            symbol: "none",
            data: [{ yAxis: 0 }],
            lineStyle: { color: "#64748b" },
          },
        },
      ],
    }),
    [points],
  );
  return <EChart option={option} className="h-64 w-full" />;
}
