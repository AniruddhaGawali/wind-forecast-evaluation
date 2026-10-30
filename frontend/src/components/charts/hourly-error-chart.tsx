"use client";

import { useMemo } from "react";

import type { HourRow } from "@/lib/api/types";

import { COLORS } from "./colors";
import { EChart, type EChartsOption } from "./echart";

/** Typical miss and bias for each hour of the day. */
export function HourlyErrorChart({ rows }: { rows: HourRow[] }) {
  const option = useMemo<EChartsOption>(
    () => ({
      animation: false,
      color: [COLORS.error, COLORS.bias],
      grid: { left: 56, right: 16, top: 40, bottom: 48 },
      legend: { top: 0 },
      tooltip: {
        trigger: "axis",
        valueFormatter: (v: number) => `${Math.round(v).toLocaleString("en-GB")} MW`,
      },
      xAxis: {
        type: "category",
        data: rows.map((r) => String(r.hour).padStart(2, "0")),
        name: "Hour of day (UTC)",
        nameLocation: "middle",
        nameGap: 30,
      },
      yAxis: { type: "value", name: "MW", nameLocation: "middle", nameGap: 40 },
      series: [
        { name: "Typical miss (MAE)", type: "bar", data: rows.map((r) => r.mae) },
        { name: "Bias", type: "bar", data: rows.map((r) => r.bias) },
      ],
    }),
    [rows],
  );
  return <EChart option={option} className="h-64 w-full" />;
}
