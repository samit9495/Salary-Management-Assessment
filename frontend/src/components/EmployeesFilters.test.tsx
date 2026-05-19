import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { EmployeesFilters } from "@/components/EmployeesFilters";

describe("EmployeesFilters", () => {
  it("uppercases the country and applies filters with non-empty values only", async () => {
    const onApply = vi.fn();
    render(<EmployeesFilters onApply={onApply} />);

    await userEvent.type(screen.getByLabelText(/search name/i), "ja");
    await userEvent.type(screen.getByLabelText(/country/i), "in");
    await userEvent.selectOptions(screen.getByLabelText(/sort/i), "-salary");
    await userEvent.click(screen.getByRole("button", { name: /apply/i }));

    expect(onApply).toHaveBeenCalledWith({ q: "ja", country: "IN", sort: "-salary" });
  });

  it("omits empty values from the apply payload", async () => {
    const onApply = vi.fn();
    render(<EmployeesFilters onApply={onApply} />);

    await userEvent.click(screen.getByRole("button", { name: /apply/i }));

    expect(onApply).toHaveBeenCalledWith({ q: undefined, country: undefined, sort: undefined });
  });
});
