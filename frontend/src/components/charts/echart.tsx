"use client";

import { BarChart, LineChart } from "echarts/charts";
import {
  AriaComponent,
  DataZoomComponent,
  MarkLineComponent,
  GridComponent,
  LegendComponent,
  TooltipComponent,
} from "echarts/components";
import * as echarts from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { useEffect, useRef } from "react";

// Register only the parts we use, to keep the bundle small.
echarts.use([
  AriaComponent,
  BarChart,
  LineChart,
  MarkLineComponent,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent,
  CanvasRenderer,
]);

export type EChartsOption = echarts.EChartsCoreOption;

interface Props {
  option: EChartsOption;
  /** What the chart shows, read out by screen readers. */
  label: string;
  className?: string;
  /** Called with the x-axis value under a click anywhere in the plot area (category label or time in ms). */
  onClickX?: (x: string | number) => void;
}

/** Thin wrapper: the rest of the app passes an option object and never touches echarts directly. */
export function EChart({ option, label, className, onClickX }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<echarts.ECharts | null>(null);
  // Kept in a ref so a new callback does not re-create the chart.
  const onClickRef = useRef(onClickX);

  useEffect(() => {
    onClickRef.current = onClickX;
  }, [onClickX]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const chart = echarts.init(container);
    chartRef.current = chart;
    // Listen on the canvas, not on series items: thin lines without symbols are hard to hit.
    chart.getZr().on("click", (event) => {
      const point = [event.offsetX, event.offsetY];
      if (!onClickRef.current || !chart.containPixel({ gridIndex: 0 }, point)) return;
      const [x] = chart.convertFromPixel({ gridIndex: 0 }, point) as number[];
      const axis = (chart.getOption().xAxis as { type?: string; data?: string[] }[])[0];
      onClickRef.current(axis.type === "category" && axis.data ? axis.data[Math.round(x)] : x);
    });
    const observer = new ResizeObserver(() => chart.resize());
    observer.observe(container);
    return () => {
      observer.disconnect();
      chart.dispose();
      chartRef.current = null;
    };
  }, []);

  useEffect(() => {
    chartRef.current?.setOption({ aria: { enabled: true }, ...option }, true);
  }, [option]);

  // ECharts writes its own generated aria-label on the chart element, so our label sits on a wrapper.
  return (
    <div role="img" aria-label={label} className={className}>
      <div
        ref={containerRef}
        className="size-full"
        style={onClickX ? { cursor: "pointer" } : undefined}
      />
    </div>
  );
}
