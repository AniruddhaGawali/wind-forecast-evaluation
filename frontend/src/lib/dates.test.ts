import { describe, expect, it } from "vitest";

import { CUTOFF_OPTIONS, sensitivityCutoffs, utcDay } from "@/lib/dates";

describe("dates", () => {
  it("offers every half hour as a cutoff", () => {
    expect(CUTOFF_OPTIONS).toHaveLength(48);
    expect(CUTOFF_OPTIONS.slice(0, 3)).toEqual(["00:00", "00:30", "01:00"]);
  });

  it("adds the current cutoff to the sensitivity set once, in order", () => {
    expect(sensitivityCutoffs("09:00")).toHaveLength(8);
    expect(sensitivityCutoffs("10:30")).toContain("10:30");
    expect(sensitivityCutoffs("10:30").indexOf("10:30")).toBe(4);
  });

  it("takes the UTC day of a target hour", () => {
    expect(utcDay("2026-01-14T23:00:00Z")).toBe("2026-01-14");
    expect(utcDay("2026-01-14T23:00:00+00:00")).toBe("2026-01-14");
  });
});
