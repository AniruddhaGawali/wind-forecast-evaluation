"use client";

import { InfoIcon } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import type { Summary } from "@/lib/api/types";
import { formatMw, formatPct } from "@/lib/format";

interface Kpi {
  label: string;
  value: string;
  help: string;
}

function kpis(s: Summary): Kpi[] {
  return [
    {
      label: "Typical miss (MAE)",
      value: formatMw(s.mae),
      help: "On average, the forecast was off by this much in either direction.",
    },
    {
      label: "Big-miss weighted (RMSE)",
      value: formatMw(s.rmse),
      help: "Like the typical miss, but large misses count more. Much higher than MAE means occasional big surprises.",
    },
    {
      label: "Bias",
      value: formatMw(s.bias, { signed: true }),
      help: "Average signed miss. Positive means the forecast expected more wind than came, so you would have been short.",
    },
    {
      label: "90% of misses below (P90)",
      value: formatMw(s.p90),
      help: "Nine hours in ten, the forecast missed by less than this. Use it to size your safety buffer.",
    },
    {
      label: "Miss vs output (WAPE)",
      value: formatPct(s.wape_pct),
      help: "Total miss as a share of total wind output.",
    },
  ];
}

export function KpiCards({ summary }: { summary: Summary }) {
  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
      {kpis(summary).map((kpi) => (
        <Card key={kpi.label} size="sm">
          <CardHeader>
            <CardTitle className="text-muted-foreground flex items-center gap-1.5 text-sm font-normal">
              {kpi.label}
              <Tooltip>
                <TooltipTrigger aria-label={`What is ${kpi.label}?`} className="cursor-help">
                  <InfoIcon className="size-3.5" />
                </TooltipTrigger>
                <TooltipContent>{kpi.help}</TooltipContent>
              </Tooltip>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-semibold tabular-nums">{kpi.value}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
