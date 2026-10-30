// Allowed delivery window and default cutoff. Keep in sync with backend/app/config.py.
export const DELIVERY_START = "2026-01-02";
export const DELIVERY_END = "2026-02-01";
export const DEFAULT_CUTOFF = "09:00";

/** Cutoff choices: every half hour. Forecasts are published at :30 past, so this covers every distinct result. */
export const CUTOFF_OPTIONS = Array.from({ length: 48 }, (_, i) => {
  const h = String(Math.floor(i / 2)).padStart(2, "0");
  return `${h}:${i % 2 ? "30" : "00"}`;
});
