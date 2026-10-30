import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { KpiCards } from "@/components/kpi-cards";
import type { Summary } from "@/lib/api/types";
import { renderWithProviders } from "@/test/utils";

const summary: Summary = {
  n: 744,
  mae: 2038.6,
  rmse: 2505.2,
  bias: 1748.3,
  p50: 1700,
  p90: 4098.4,
  p95: 4600,
  wape_pct: 18.06,
};

describe("KpiCards", () => {
  it("shows each headline number formatted in MW", () => {
    renderWithProviders(<KpiCards summary={summary} />);
    expect(screen.getByText("2,039 MW")).toBeInTheDocument();
    expect(screen.getByText("2,505 MW")).toBeInTheDocument();
    expect(screen.getByText("+1,748 MW")).toBeInTheDocument();
    expect(screen.getByText("4,098 MW")).toBeInTheDocument();
    expect(screen.getByText("18.1%")).toBeInTheDocument();
  });

  it("gives every metric a labelled help button", () => {
    renderWithProviders(<KpiCards summary={summary} />);
    expect(screen.getAllByRole("button", { name: /^What is/ })).toHaveLength(5);
  });

  it("shows a dash when a metric is missing", () => {
    renderWithProviders(<KpiCards summary={{ ...summary, n: 0, mae: null, wape_pct: null }} />);
    expect(screen.getAllByText("–")).toHaveLength(2);
  });
});
