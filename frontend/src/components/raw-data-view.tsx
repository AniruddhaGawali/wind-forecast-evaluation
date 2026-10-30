"use client";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useRawData } from "@/hooks/use-raw-data";

import { RawChart } from "./charts/raw-chart";

export function RawDataView({ start, end }: { start: string; end: string }) {
  const { data, error, isPending, isFetching, refetch } = useRawData(start, end);

  if (!start || !end || start > end) {
    return (
      <Alert>
        <AlertTitle>Pick a date range</AlertTitle>
        <AlertDescription>Choose a start date that is on or before the end date.</AlertDescription>
      </Alert>
    );
  }
  if (isPending) return <Skeleton className="h-[420px] w-full" />;
  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Could not load data</AlertTitle>
        <AlertDescription className="flex items-center gap-3">
          {error.message}
          <Button size="sm" variant="outline" onClick={() => refetch()} disabled={isFetching}>
            Retry
          </Button>
        </AlertDescription>
      </Alert>
    );
  }
  if (data.actuals.length === 0) {
    return (
      <Alert>
        <AlertTitle>No data</AlertTitle>
        <AlertDescription>There is no wind data for this range.</AlertDescription>
      </Alert>
    );
  }
  return (
    <div className="space-y-2">
      <RawChart data={data} />
      <p className="text-muted-foreground text-sm">
        {data.actuals.length} actual half-hours and {data.forecasts.length} forecast hours shown.
      </p>
    </div>
  );
}
