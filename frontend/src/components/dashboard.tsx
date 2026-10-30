"use client";

import { LightbulbIcon } from "lucide-react";

import { ErrorHistogram } from "@/components/charts/error-histogram";
import { ErrorTimeChart } from "@/components/charts/error-time-chart";
import { ForecastChart } from "@/components/charts/forecast-chart";
import { HourlyErrorChart } from "@/components/charts/hourly-error-chart";
import { KpiCards } from "@/components/kpi-cards";
import { QueryState } from "@/components/query-state";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useMetrics, useSeries } from "@/hooks/use-analysis";
import type { AnalysisParams, Coverage } from "@/lib/api/types";

function CoverageBadge({ coverage }: { coverage: Coverage }) {
  const complete = coverage.skipped === 0;
  return (
    <Badge variant={complete ? "secondary" : "destructive"}>
      {coverage.scored} of {coverage.expected} hours scored
      {complete
        ? ""
        : ` · ${coverage.skipped} skipped (${coverage.missing_forecast} no forecast, ${coverage.missing_actual} no actual)`}
    </Badge>
  );
}

export function Dashboard({ params }: { params: AnalysisParams }) {
  const metrics = useMetrics(params);
  const series = useSeries(params);

  return (
    <div className="space-y-6">
      <QueryState
        isPending={metrics.isPending}
        error={metrics.error}
        onRetry={() => metrics.refetch()}
        isEmpty={metrics.data?.coverage.scored === 0}
        skeletonClassName="h-48 w-full"
      >
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

      <Card>
        <CardHeader>
          <CardTitle>Actual wind vs the forecast you would have had</CardTitle>
          <CardDescription>
            For each hour, the latest forecast published before the decision time. Scroll or drag
            the slider to zoom.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <QueryState
            isPending={series.isPending}
            error={series.error}
            onRetry={() => series.refetch()}
            isEmpty={series.data?.points.length === 0}
            skeletonClassName="h-[420px] w-full"
          >
            {series.data && <ForecastChart points={series.data.points} />}
          </QueryState>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Error over time</CardTitle>
          <CardDescription>
            Forecast minus actual. Above zero: forecast too high (you would be short).
          </CardDescription>
        </CardHeader>
        <CardContent>
          <QueryState
            isPending={series.isPending}
            error={series.error}
            onRetry={() => series.refetch()}
            isEmpty={series.data?.points.length === 0}
            skeletonClassName="h-64 w-full"
          >
            {series.data && <ErrorTimeChart points={series.data.points} />}
          </QueryState>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>How big are the misses?</CardTitle>
            <CardDescription>Number of hours per 0.5 GW error band (labels in GW).</CardDescription>
          </CardHeader>
          <CardContent>
            <QueryState
              isPending={metrics.isPending}
              error={metrics.error}
              onRetry={() => metrics.refetch()}
              isEmpty={metrics.data?.coverage.scored === 0}
              skeletonClassName="h-64 w-full"
            >
              {metrics.data && <ErrorHistogram bins={metrics.data.error_histogram} />}
            </QueryState>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Which hours are worst?</CardTitle>
            <CardDescription>Typical miss and bias by hour of day (UTC).</CardDescription>
          </CardHeader>
          <CardContent>
            <QueryState
              isPending={metrics.isPending}
              error={metrics.error}
              onRetry={() => metrics.refetch()}
              isEmpty={metrics.data?.coverage.scored === 0}
              skeletonClassName="h-64 w-full"
            >
              {metrics.data && <HourlyErrorChart rows={metrics.data.by_hour_of_day} />}
            </QueryState>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
