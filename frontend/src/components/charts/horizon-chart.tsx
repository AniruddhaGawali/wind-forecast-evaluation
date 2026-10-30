"use client";

import { useMemo } from "react";

import type { HorizonRow } from "@/lib/api/types";

import { COLORS, mwTooltip } from "./colors";
import { EChart, type EChartsOption } from "./echart";

/** Error by forecast age: hours between the forecast's publish time and the hour it predicts. */
export function HorizonChart({ rows }: { rows: HorizonRow[] }) {
  const option = useMemo<EChartsOption>(
    () => ({
      animation: false,
      color: [COLORS.error, COLORS.forecast],
      grid: { left: 56, right: 16, top: 40, bottom: 48 },
      legend: { top: 0 },
      tooltip: {
        trigger: "axis",
        valueFormatter: mwTooltip,
        // Show how many hours sit behind each bucket: a bucket with few hours is noisy.
        formatter: (
          items: {
            axisValue: string;
            dataIndex: number;
            marker: string;
            seriesName: string;
            value: number;
          }[],
        ) =>
          [
            `${items[0].axisValue} old · ${rows[items[0].dataIndex].n} hours`,
            ...items.map((i) => `${i.marker}${i.seriesName}: ${mwTooltip(i.value)}`),
          ].join("<br/>"),
      },
      xAxis: {
        type: "category",
        data: rows.map((r) => r.horizon),
        name: "Forecast age (hours before the target hour)",
        nameLocation: "middle",
        nameGap: 30,
      },
      yAxis: { type: "value", name: "MW", nameLocation: "middle", nameGap: 40 },
      series: [
        { name: "Typical miss (MAE)", type: "bar", data: rows.map((r) => r.mae) },
        { name: "Buffer for 90% (P90)", type: "bar", data: rows.map((r) => r.p90) },
      ],
    }),
    [rows],
  );
  return (
    <EChart
      option={option}
      label="Typical miss and P90 error by forecast age"
      className="h-64 w-full"
    />
  );
}
