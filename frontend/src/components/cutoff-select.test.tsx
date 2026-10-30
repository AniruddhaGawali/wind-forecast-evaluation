import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { CutoffSelect } from "@/components/cutoff-select";

describe("CutoffSelect", () => {
  it("is labelled and shows the current value", () => {
    render(<CutoffSelect value="09:00" onChange={() => {}} />);
    expect(screen.getByLabelText("Decision time (day before, UK)")).toHaveTextContent("09:00");
  });

  it("reports the picked cutoff", async () => {
    const onChange = vi.fn();
    render(<CutoffSelect value="09:00" onChange={onChange} />);
    await userEvent.click(screen.getByLabelText("Decision time (day before, UK)"));
    await userEvent.click(await screen.findByRole("option", { name: "12:00" }));
    expect(onChange).toHaveBeenCalledWith("12:00");
  });
});
