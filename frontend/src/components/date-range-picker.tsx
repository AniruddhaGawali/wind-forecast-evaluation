"use client";

import { format, parseISO } from "date-fns";
import { CalendarIcon } from "lucide-react";
import { useState } from "react";
import type { DateRange } from "react-day-picker";

import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Label } from "@/components/ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { DELIVERY_END, DELIVERY_START } from "@/lib/dates";

const ISO = "yyyy-MM-dd";
const MIN = parseISO(DELIVERY_START);
const MAX = parseISO(DELIVERY_END);

interface Props {
  start: string;
  end: string;
  onChange: (range: { start: string; end: string }) => void;
}

export function DateRangePicker({ start, end, onChange }: Props) {
  const [open, setOpen] = useState(false);
  // While the user has clicked only the first day, the range is incomplete: keep it as a draft.
  const [draft, setDraft] = useState<DateRange | undefined>();

  const committed: DateRange = { from: parseISO(start), to: parseISO(end) };
  const selected = draft ?? committed;

  // First click starts a fresh range; second click completes it (in either order).
  function handleDayClick(day: Date) {
    if (!draft?.from) {
      setDraft({ from: day, to: undefined });
      return;
    }
    const [from, to] = day < draft.from ? [day, draft.from] : [draft.from, day];
    setDraft(undefined);
    onChange({ start: format(from, ISO), end: format(to, ISO) });
    setOpen(false);
  }

  return (
    <div className="grid gap-1.5">
      <Label htmlFor="date-range">Delivery dates (UTC)</Label>
      <Popover
        open={open}
        onOpenChange={(next) => {
          setOpen(next);
          if (!next) setDraft(undefined);
        }}
      >
        <PopoverTrigger
          render={
            <Button id="date-range" variant="outline" className="w-72 justify-start font-normal" />
          }
        >
          <CalendarIcon />
          {format(committed.from!, "d MMM yyyy")} – {format(committed.to!, "d MMM yyyy")}
        </PopoverTrigger>
        <PopoverContent align="start" className="w-auto p-0">
          <Calendar
            mode="range"
            numberOfMonths={2}
            defaultMonth={committed.from}
            selected={selected}
            onDayClick={handleDayClick}
            startMonth={MIN}
            endMonth={MAX}
            disabled={{ before: MIN, after: MAX }}
          />
        </PopoverContent>
      </Popover>
    </div>
  );
}
