"use client";

import { useMemo } from "react";

import type { RawResponse } from "@/lib/api/types";

import { EChart, type EChartsOption } from "./echart";

const ACTUAL_COLOR = "#2563eb";
const FORECAST_COLOR = "#f97316";

export function RawChart({ data }: { data: RawResponse }) {
  const option = useMemo<EChartsOption>(
    () => ({
      animation: false,
      color: [ACTUAL_COLOR, FORECAST_COLOR],
      grid: { left: 64, right: 24, top: 40, bottom: 96 },
      legend: { top: 0 },
      tooltip: { trigger: "axis" },
      xAxis: { type: "time", name: "Time (UTC)", nameLocation: "middle", nameGap: 30 },
      yAxis: { type: "value", name: "Wind generation (MW)", nameLocation: "middle", nameGap: 48 },
      dataZoom: [{ type: "inside" }, { type: "slider", height: 24, bottom: 8 }],
      series: [
        {
          name: "Actual (half-hourly)",
          type: "line",
          showSymbol: false,
          sampling: "lttb",
          data: data.actuals.map((p) => [p.start_time, p.generation_mw]),
        },
        {
          name: "Latest forecast (hourly)",
          type: "scatter",
          symbolSize: 5,
          data: data.forecasts.map((p) => [p.start_time, p.generation_mw]),
        },
      ],
    }),
    [data],
  );

  return <EChart option={option} className="h-[420px] w-full" />;
}
