import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import Home from "@/app/page";
import { renderWithProviders } from "@/test/utils";

// Canvas charts cannot draw in jsdom; this test is about requests, not pixels.
vi.mock("@/components/charts/echart", () => ({
  EChart: ({ label }: { label: string }) => <div role="img" aria-label={label} />,
}));

const summary = {
  n: 0,
  mae: null,
  rmse: null,
  bias: null,
  p50: null,
  p90: null,
  p95: null,
  wape_pct: null,
};
const coverage = { expected: 0, scored: 0, skipped: 0, missing_forecast: 0, missing_actual: 0 };

function fakeResponse(url: string) {
  const path = new URL(url).pathname;
  const body =
    path === "/api/v1/series"
      ? { cutoff: "09:00", start: "", end: "", coverage, points: [] }
      : path === "/api/v1/sensitivity"
        ? { start: "", end: "", results: [] }
        : {
            cutoff: "09:00",
            start: "",
            end: "",
            coverage,
            summary,
            by_hour_of_day: [],
            by_day: [],
            by_horizon: [],
            by_generation_level: [],
            error_histogram: [],
            recommendation: { buffer_mw: null, text: "" },
          };
  return Promise.resolve(new Response(JSON.stringify(body)));
}

const cutoffsRequested = (fetchMock: ReturnType<typeof vi.fn>, path: string) =>
  fetchMock.mock.calls
    .map(([url]) => new URL(url as string))
    .filter((u) => u.pathname === path)
    .map((u) => u.searchParams.get("cutoff"));

describe("Home", () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    fetchMock = vi.fn((url: string) => fakeResponse(url));
    vi.stubGlobal("fetch", fetchMock);
  });
  afterEach(() => vi.unstubAllGlobals());

  it("requests new metrics and series when the cutoff changes", async () => {
    renderWithProviders(<Home />);
    await waitFor(() => expect(cutoffsRequested(fetchMock, "/api/v1/metrics")).toEqual(["09:00"]));

    await userEvent.click(screen.getByLabelText("Decision time (day before, UK)"));
    await userEvent.click(await screen.findByRole("option", { name: "12:00" }));

    await waitFor(() => {
      expect(cutoffsRequested(fetchMock, "/api/v1/metrics")).toEqual(["09:00", "12:00"]);
      expect(cutoffsRequested(fetchMock, "/api/v1/series")).toEqual(["09:00", "12:00"]);
    });
  });

  it("shows the server error with a retry button that asks again", async () => {
    fetchMock.mockImplementation(() =>
      Promise.resolve(new Response(JSON.stringify({ detail: "Data not loaded" }), { status: 503 })),
    );
    renderWithProviders(<Home />);
    const retries = await screen.findAllByRole("button", { name: "Retry" });
    expect(screen.getAllByText("Data not loaded").length).toBeGreaterThan(0);

    const before = fetchMock.mock.calls.length;
    await userEvent.click(retries[0]);
    await waitFor(() => expect(fetchMock.mock.calls.length).toBeGreaterThan(before));
  });
});
