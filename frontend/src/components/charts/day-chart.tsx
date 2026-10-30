"use client";

import { useMemo } from "react";

import type { SeriesPoint } from "@/lib/api/types";

import { COLORS, mwTooltip } from "./colors";
import { EChart, type EChartsOption } from "./echart";

const hourLabel = (time: string) => new Date(time).toISOString().slice(11, 16);

/** One day: actual and forecast as lines, the error per hour as bars underneath. */
export function DayChart({ points }: { points: SeriesPoint[] }) {
  const option = useMemo<EChartsOption>(
    () => ({
      animation: false,
      color: [COLORS.actual, COLORS.forecast, COLORS.error],
      grid: { left: 64, right: 16, top: 40, bottom: 48 },
      legend: { top: 0 },
      tooltip: { trigger: "axis", valueFormatter: mwTooltip },
      xAxis: {
        type: "category",
        data: points.map((p) => hourLabel(p.time)),
        name: "Hour (UTC)",
        nameLocation: "middle",
        nameGap: 30,
      },
      yAxis: { type: "value", name: "MW", nameLocation: "middle", nameGap: 48 },
      series: [
        { name: "Actual", type: "line", data: points.map((p) => p.actual_mw) },
        {
          name: "Forecast at decision time",
          type: "line",
          lineStyle: { type: "dashed" },
          data: points.map((p) => p.forecast_mw),
        },
        {
          name: "Forecast - actual",
          type: "bar",
          barMaxWidth: 14,
          data: points.map((p) => p.error_mw),
        },
      ],
    }),
    [points],
  );
  return (
    <EChart
      option={option}
      label="Actual, forecast and error for each hour of the chosen day"
      className="h-72 w-full"
    />
  );
}
