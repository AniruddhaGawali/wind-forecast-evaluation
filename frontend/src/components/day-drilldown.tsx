"use client";

import { format, parseISO } from "date-fns";

import { DayChart } from "@/components/charts/day-chart";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { DayRow, SeriesPoint } from "@/lib/api/types";
import { utcDay } from "@/lib/dates";
import { formatMw } from "@/lib/format";

const dayLabel = (day: string) => format(parseISO(day), "EEE d MMM");

interface Props {
  points: SeriesPoint[];
  days: DayRow[];
  day: string;
  onDayChange: (day: string) => void;
}

/** One day hour by hour: pick a day (or click the main chart) to see where the forecast went wrong. */
export function DayDrilldown({ points, days, day, onDayChange }: Props) {
  // by_day uses the UK delivery day; in January UK time equals UTC, so the UTC day of each hour matches.
  const dayPoints = points.filter((p) => utcDay(p.time) === day);
  const stats = days.find((d) => d.day === day);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end gap-x-6 gap-y-3">
        <div className="grid gap-1.5">
          <Label htmlFor="drilldown-day">Day</Label>
          <Select value={day} onValueChange={(next) => next && onDayChange(next as string)}>
            <SelectTrigger id="drilldown-day" className="w-40">
              <SelectValue>{dayLabel(day)}</SelectValue>
            </SelectTrigger>
            <SelectContent>
              {days.map((d) => (
                <SelectItem key={d.day} value={d.day}>
                  {dayLabel(d.day)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        {stats && (
          <dl className="flex flex-wrap gap-x-6 gap-y-1 text-sm">
            {[
              ["Typical miss", formatMw(stats.mae)],
              ["Bias", formatMw(stats.bias, { signed: true })],
              [
                "Worst hour",
                formatMw(
                  dayPoints.length ? Math.max(...dayPoints.map((p) => Math.abs(p.error_mw))) : null,
                ),
              ],
              ["Hours scored", String(stats.n)],
            ].map(([term, value]) => (
              <div key={term}>
                <dt className="text-muted-foreground">{term}</dt>
                <dd className="font-medium tabular-nums">{value}</dd>
              </div>
            ))}
          </dl>
        )}
      </div>

      <DayChart points={dayPoints} />

      <div className="max-h-80 overflow-auto rounded-md border">
        <Table>
          <caption className="sr-only">
            Hourly actual, forecast and error for {dayLabel(day)}
          </caption>
          <TableHeader className="bg-background sticky top-0">
            <TableRow>
              <TableHead>Hour (UTC)</TableHead>
              <TableHead className="text-right">Actual</TableHead>
              <TableHead className="text-right">Forecast</TableHead>
              <TableHead className="text-right">Error</TableHead>
              <TableHead className="text-right">Forecast age</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody className="tabular-nums">
            {dayPoints.map((p) => (
              <TableRow key={p.time}>
                <TableCell>{new Date(p.time).toISOString().slice(11, 16)}</TableCell>
                <TableCell className="text-right">{formatMw(p.actual_mw)}</TableCell>
                <TableCell className="text-right">{formatMw(p.forecast_mw)}</TableCell>
                <TableCell className="text-right">
                  {formatMw(p.error_mw, { signed: true })}
                </TableCell>
                <TableCell className="text-right">{Math.round(p.horizon_h)} h</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
