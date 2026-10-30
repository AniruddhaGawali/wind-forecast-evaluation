// Allowed delivery window and default cutoff. Keep in sync with backend/app/config.py.
export const DELIVERY_START = "2026-01-02";
export const DELIVERY_END = "2026-02-01";
export const DEFAULT_CUTOFF = "09:00";

/** Cutoff choices: every half hour. Forecasts are published at :30 past, so this covers every distinct result. */
export const CUTOFF_OPTIONS = Array.from({ length: 48 }, (_, i) => {
  const h = String(Math.floor(i / 2)).padStart(2, "0");
  return `${h}:${i % 2 ? "30" : "00"}`;
});

/** Cutoffs compared in the sensitivity chart: every three hours across the day before. */
export const SENSITIVITY_CUTOFFS = [
  "00:00",
  "03:00",
  "06:00",
  "09:00",
  "12:00",
  "15:00",
  "18:00",
  "21:00",
];

/** The sensitivity set plus the user's current cutoff, so it can be highlighted. Sorted, no duplicates. */
export function sensitivityCutoffs(current: string): string[] {
  return [...new Set([...SENSITIVITY_CUTOFFS, current])].sort();
}

/** "2026-01-14T05:00:00Z" -> "2026-01-14" (the UTC day of a target hour). */
export function utcDay(time: string | number): string {
  return new Date(time).toISOString().slice(0, 10);
}
