"use client";

import { useIsFetching } from "@tanstack/react-query";
import { Loader2Icon } from "lucide-react";
import { useState } from "react";

import { AboutPanel } from "@/components/about-panel";
import { CutoffSelect } from "@/components/cutoff-select";
import { Dashboard } from "@/components/dashboard";
import { DateRangePicker } from "@/components/date-range-picker";
import { DEFAULT_CUTOFF, DELIVERY_END, DELIVERY_START } from "@/lib/dates";

export default function Home() {
  const [range, setRange] = useState({ start: DELIVERY_START, end: DELIVERY_END });
  const [cutoff, setCutoff] = useState(DEFAULT_CUTOFF);
  const fetching = useIsFetching() > 0;

  return (
    <div className="flex min-h-full flex-col">
      <header className="border-b px-4 py-4 sm:px-6">
        <h1 className="text-xl font-semibold">Wind Forecast Evaluation Portal</h1>
        <p className="text-muted-foreground text-sm">
          How wrong was the day-ahead GB wind forecast you could have used? January 2026 delivery.
          Chart times are UTC.{" "}
          <a href="#about" className="text-foreground underline underline-offset-4">
            How this works
          </a>
        </p>
      </header>
      <main className="mx-auto w-full max-w-6xl flex-1 space-y-6 p-4 sm:p-6">
        <div className="flex flex-wrap items-end gap-4">
          <DateRangePicker {...range} onChange={setRange} />
          <CutoffSelect value={cutoff} onChange={setCutoff} />
          <p
            role="status"
            aria-live="polite"
            className="text-muted-foreground flex h-8 items-center gap-1.5 text-sm"
          >
            {fetching && (
              <>
                <Loader2Icon className="size-4 animate-spin" aria-hidden />
                Updating…
              </>
            )}
          </p>
        </div>
        <Dashboard params={{ ...range, cutoff }} onCutoffChange={setCutoff} />
        <AboutPanel />
      </main>
    </div>
  );
}
