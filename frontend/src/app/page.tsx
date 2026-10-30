"use client";

import { useState } from "react";

import { CutoffSelect } from "@/components/cutoff-select";
import { Dashboard } from "@/components/dashboard";
import { DateRangePicker } from "@/components/date-range-picker";
import { DEFAULT_CUTOFF, DELIVERY_END, DELIVERY_START } from "@/lib/dates";

export default function Home() {
  const [range, setRange] = useState({ start: DELIVERY_START, end: DELIVERY_END });
  const [cutoff, setCutoff] = useState(DEFAULT_CUTOFF);

  return (
    <div className="flex min-h-full flex-col">
      <header className="border-b px-6 py-4">
        <h1 className="text-xl font-semibold">Wind Forecast Evaluation Portal</h1>
        <p className="text-muted-foreground text-sm">
          How wrong was the day-ahead GB wind forecast you could have used? January 2026 delivery.
          Chart times are UTC.
        </p>
      </header>
      <main className="mx-auto w-full max-w-6xl flex-1 space-y-6 p-6">
        <div className="flex flex-wrap items-end gap-4">
          <DateRangePicker {...range} onChange={setRange} />
          <CutoffSelect value={cutoff} onChange={setCutoff} />
        </div>
        <Dashboard params={{ ...range, cutoff }} />
      </main>
    </div>
  );
}
