"use client";

import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { CUTOFF_OPTIONS } from "@/lib/dates";

interface Props {
  value: string;
  onChange: (value: string) => void;
}

export function CutoffSelect({ value, onChange }: Props) {
  return (
    <div className="grid gap-1.5">
      <Label htmlFor="cutoff">Decision time (day before, UK)</Label>
      <Select value={value} onValueChange={(next) => next && onChange(next as string)}>
        <SelectTrigger id="cutoff" className="w-40">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {CUTOFF_OPTIONS.map((option) => (
            <SelectItem key={option} value={option}>
              {option}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
