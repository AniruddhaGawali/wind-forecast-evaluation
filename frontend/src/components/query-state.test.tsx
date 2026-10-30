import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { QueryState } from "@/components/query-state";

const props = { isPending: false, error: null, onRetry: () => {} };

describe("QueryState", () => {
  it("shows the error message and retries on click", async () => {
    const onRetry = vi.fn();
    render(
      <QueryState {...props} error={new Error("Cannot reach the server.")} onRetry={onRetry}>
        <p>data</p>
      </QueryState>,
    );
    expect(screen.getByText("Could not load data")).toBeInTheDocument();
    expect(screen.getByText("Cannot reach the server.")).toBeInTheDocument();
    expect(screen.queryByText("data")).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Retry" }));
    expect(onRetry).toHaveBeenCalledOnce();
  });

  it("shows an empty message instead of children when there is nothing to score", () => {
    render(
      <QueryState {...props} isEmpty>
        <p>data</p>
      </QueryState>,
    );
    expect(screen.getByText("No data")).toBeInTheDocument();
    expect(screen.queryByText("data")).not.toBeInTheDocument();
  });

  it("renders children once data is there", () => {
    render(
      <QueryState {...props}>
        <p>data</p>
      </QueryState>,
    );
    expect(screen.getByText("data")).toBeInTheDocument();
  });
});
