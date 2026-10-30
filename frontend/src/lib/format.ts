const mw = new Intl.NumberFormat("en-GB", { maximumFractionDigits: 0 });

/** 4098.4 -> "4,098 MW"; null -> "–". */
export function formatMw(value: number | null, { signed = false } = {}): string {
  if (value === null) return "–";
  const sign = signed && value > 0 ? "+" : "";
  return `${sign}${mw.format(value)} MW`;
}

export function formatPct(value: number | null): string {
  return value === null ? "–" : `${value.toFixed(1)}%`;
}
