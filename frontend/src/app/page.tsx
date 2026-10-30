"use client";

import { useState } from "react";

import { DateRangePicker } from "@/components/date-range-picker";
import { RawDataView } from "@/components/raw-data-view";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { DELIVERY_START } from "@/lib/dates";

export default function Home() {
  const [range, setRange] = useState({ start: DELIVERY_START, end: "2026-01-08" });

  return (
    <div className="flex min-h-full flex-col">
      <header className="border-b px-6 py-4">
        <h1 className="text-xl font-semibold">Wind Forecast Evaluation Portal</h1>
        <p className="text-muted-foreground text-sm">
          GB national wind, January 2026 delivery. All times UTC.
        </p>
      </header>
      <main className="mx-auto w-full max-w-6xl flex-1 space-y-6 p-6">
        <DateRangePicker {...range} onChange={setRange} />
        <Card>
          <CardHeader>
            <CardTitle>Actual wind vs latest forecast</CardTitle>
            <CardDescription>
              Raw data check. Lines are measured output; dots are the latest forecast made before
              each hour.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <RawDataView {...range} />
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
