"use client";

import { useMemo } from "react";

import type { SeriesPoint } from "@/lib/api/types";

import { COLORS, MW_AXIS } from "./colors";
import { EChart, type EChartsOption } from "./echart";

/** Actual wind vs the forecast chosen at the cutoff, hour by hour, with zoom. */
export function ForecastChart({ points }: { points: SeriesPoint[] }) {
  const option = useMemo<EChartsOption>(
    () => ({
      animation: false,
      color: [COLORS.actual, COLORS.forecast],
      grid: { left: 64, right: 24, top: 40, bottom: 96 },
      legend: { top: 0 },
      tooltip: {
        trigger: "axis",
        valueFormatter: (v: number) => `${Math.round(v).toLocaleString("en-GB")} MW`,
      },
      xAxis: { type: "time", name: "Target hour (UTC)", nameLocation: "middle", nameGap: 30 },
      yAxis: { ...MW_AXIS, name: "Wind generation (MW)", nameLocation: "middle", nameGap: 48 },
      dataZoom: [{ type: "inside" }, { type: "slider", height: 24, bottom: 8 }],
      series: [
        {
          name: "Actual",
          type: "line",
          showSymbol: false,
          data: points.map((p) => [p.time, p.actual_mw]),
        },
        {
          name: "Forecast at decision time",
          type: "line",
          showSymbol: false,
          lineStyle: { type: "dashed" },
          data: points.map((p) => [p.time, p.forecast_mw]),
        },
      ],
    }),
    [points],
  );
  return <EChart option={option} className="h-[420px] w-full" />;
}
