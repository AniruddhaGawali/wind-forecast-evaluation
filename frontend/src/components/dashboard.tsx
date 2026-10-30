"use client";

import { LightbulbIcon } from "lucide-react";
import { useRef, useState } from "react";

import { ErrorHistogram } from "@/components/charts/error-histogram";
import { ErrorTimeChart } from "@/components/charts/error-time-chart";
import { ForecastChart } from "@/components/charts/forecast-chart";
import { HorizonChart } from "@/components/charts/horizon-chart";
import { HourlyErrorChart } from "@/components/charts/hourly-error-chart";
import { DayDrilldown } from "@/components/day-drilldown";
import { KpiCards } from "@/components/kpi-cards";
import { QueryState } from "@/components/query-state";
import { Section } from "@/components/section";
import { SensitivityPanel } from "@/components/sensitivity-panel";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { useMetrics, useSeries } from "@/hooks/use-analysis";
import type { AnalysisParams, Coverage, DayRow } from "@/lib/api/types";

function CoverageBadge({ coverage }: { coverage: Coverage }) {
  const complete = coverage.skipped === 0;
  return (
    <Badge variant={complete ? "secondary" : "destructive"} className="h-auto whitespace-normal">
      {coverage.scored} of {coverage.expected} hours scored
      {complete
        ? ""
        : ` · ${coverage.skipped} skipped (${coverage.missing_forecast} no forecast, ${coverage.missing_actual} no actual)`}
    </Badge>
  );
}

/** The day to drill into: the user's pick if it is still in range, otherwise the worst day. */
function activeDay(picked: string | null, days: DayRow[]): string | null {
  if (picked && days.some((d) => d.day === picked)) return picked;
  return (
    days.reduce<DayRow | null>(
      (worst, d) => (!worst || (d.mae ?? 0) > (worst.mae ?? 0) ? d : worst),
      null,
    )?.day ?? null
  );
}

interface Props {
  params: AnalysisParams;
  onCutoffChange: (cutoff: string) => void;
}

export function Dashboard({ params, onCutoffChange }: Props) {
  const metrics = useMetrics(params);
  const series = useSeries(params);
  const [pickedDay, setPickedDay] = useState<string | null>(null);
  const drilldownRef = useRef<HTMLDivElement>(null);
  const day = activeDay(pickedDay, metrics.data?.by_day ?? []);

  // Clicking a chart opens that day below and moves the view (and keyboard focus) to it.
  function openDay(next: string) {
    setPickedDay(next);
    drilldownRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    drilldownRef.current?.focus({ preventScroll: true });
  }

  const metricsState = {
    isPending: metrics.isPending,
    error: metrics.error,
    onRetry: () => metrics.refetch(),
    isEmpty: metrics.data?.coverage.scored === 0,
  };
  const seriesState = {
    isPending: series.isPending,
    error: series.error,
    onRetry: () => series.refetch(),
    isEmpty: series.data?.points.length === 0,
  };

  return (
    <div className="space-y-6">
      <QueryState {...metricsState} skeletonClassName="h-48 w-full">
        {metrics.data && (
          <div className="space-y-4">
            <Alert>
              <LightbulbIcon />
              <AlertTitle>Recommendation</AlertTitle>
              <AlertDescription>
                {metrics.data.recommendation.text} Deciding at {metrics.data.cutoff} UK time the day
                before.
              </AlertDescription>
            </Alert>
            <KpiCards summary={metrics.data.summary} />
            <CoverageBadge coverage={metrics.data.coverage} />
          </div>
        )}
      </QueryState>

      <Section
        title="Actual wind vs the forecast you would have had"
        description="For each hour, the latest forecast published before the decision time. Scroll or drag the slider to zoom; click to open that day below."
      >
        <QueryState {...seriesState} skeletonClassName="h-80 w-full sm:h-[420px]">
          {series.data && <ForecastChart points={series.data.points} onDayClick={openDay} />}
        </QueryState>
      </Section>

      <Section
        title="Error over time"
        description="Forecast minus actual. Above zero: forecast too high (you would be short). Click to open that day."
      >
        <QueryState {...seriesState} skeletonClassName="h-64 w-full">
          {series.data && <ErrorTimeChart points={series.data.points} onDayClick={openDay} />}
        </QueryState>
      </Section>

      <div ref={drilldownRef} tabIndex={-1} className="scroll-mt-4 rounded-xl outline-none">
        <Section
          title="Day drill-down"
          description="Every hour of one day. Opens on the worst day; pick another or click a chart above."
        >
          <QueryState
            {...seriesState}
            isPending={seriesState.isPending || metricsState.isPending}
            error={series.error ?? metrics.error}
            isEmpty={seriesState.isEmpty || day === null}
            skeletonClassName="h-96 w-full"
          >
            {series.data && metrics.data && day && (
              <DayDrilldown
                points={series.data.points}
                days={metrics.data.by_day}
                day={day}
                onDayChange={setPickedDay}
              />
            )}
          </QueryState>
        </Section>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Section
          title="Does deciding later help?"
          description="Typical miss and the 90% buffer for different decision times on the same dates. Click a bar to use that time."
        >
          <SensitivityPanel params={params} onCutoffChange={onCutoffChange} />
        </Section>
        <Section
          title="Does forecast age matter?"
          description="Error grouped by how many hours before the target hour the forecast was published."
        >
          <QueryState {...metricsState} skeletonClassName="h-64 w-full">
            {metrics.data && <HorizonChart rows={metrics.data.by_horizon} />}
          </QueryState>
        </Section>
        <Section
          title="How big are the misses?"
          description="Number of hours per 0.5 GW error band (labels in GW)."
        >
          <QueryState {...metricsState} skeletonClassName="h-64 w-full">
            {metrics.data && <ErrorHistogram bins={metrics.data.error_histogram} />}
          </QueryState>
        </Section>
        <Section
          title="Which hours are worst?"
          description="Typical miss and bias by hour of day (UTC)."
        >
          <QueryState {...metricsState} skeletonClassName="h-64 w-full">
            {metrics.data && <HourlyErrorChart rows={metrics.data.by_hour_of_day} />}
          </QueryState>
        </Section>
      </div>
    </div>
  );
}
