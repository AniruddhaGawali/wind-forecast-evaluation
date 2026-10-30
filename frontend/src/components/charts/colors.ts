// One colour per meaning, used by every chart.
export const COLORS = {
  actual: "#2563eb",
  forecast: "#f97316",
  error: "#7c3aed",
  bias: "#94a3b8",
} as const;

/** Tooltip formatter shared by every MW chart: 4098.4 -> "4,098 MW". */
export const mwTooltip = (v: number) => `${Math.round(v).toLocaleString("en-GB")} MW`;
