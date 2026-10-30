"use client";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

interface Props {
  isPending: boolean;
  error: Error | null;
  onRetry: () => void;
  isEmpty?: boolean;
  skeletonClassName?: string;
  children: React.ReactNode;
}

/** Shows loading, error (with retry) and empty states; renders children only when there is data. */
export function QueryState({
  isPending,
  error,
  onRetry,
  isEmpty,
  skeletonClassName,
  children,
}: Props) {
  if (isPending) return <Skeleton className={skeletonClassName ?? "h-80 w-full"} />;
  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Could not load data</AlertTitle>
        <AlertDescription className="flex flex-wrap items-center gap-3">
          {error.message}
          <Button size="sm" variant="outline" onClick={onRetry}>
            Retry
          </Button>
        </AlertDescription>
      </Alert>
    );
  }
  if (isEmpty) {
    return (
      <Alert>
        <AlertTitle>No data</AlertTitle>
        <AlertDescription>No hours could be scored for this range and cutoff.</AlertDescription>
      </Alert>
    );
  }
  return <>{children}</>;
}
