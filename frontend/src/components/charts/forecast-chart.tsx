"use client";

import { useMemo } from "react";

import type { SeriesPoint } from "@/lib/api/types";
import { utcDay } from "@/lib/dates";

import { COLORS, mwTooltip } from "./colors";
import { EChart, type EChartsOption } from "./echart";

/** Actual wind vs the forecast chosen at the cutoff, hour by hour, with zoom. */
export function ForecastChart({
  points,
  onDayClick,
}: {
  points: SeriesPoint[];
  /** Called with the UTC day (YYYY-MM-DD) of the clicked hour. */
  onDayClick?: (day: string) => void;
}) {
  const option = useMemo<EChartsOption>(
    () => ({
      animation: false,
      color: [COLORS.actual, COLORS.forecast],
      grid: { left: 64, right: 24, top: 40, bottom: 96 },
      legend: { top: 0 },
      tooltip: { trigger: "axis", valueFormatter: mwTooltip },
      xAxis: { type: "time", name: "Target hour (UTC)", nameLocation: "middle", nameGap: 30 },
      yAxis: { type: "value", name: "Wind generation (MW)", nameLocation: "middle", nameGap: 48 },
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
  return (
    <EChart
      option={option}
      label="Actual wind generation against the forecast available at the decision time, hourly"
      className="h-80 w-full sm:h-[420px]"
      onClickX={onDayClick && ((x) => onDayClick(utcDay(x)))}
    />
  );
}
