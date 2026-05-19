import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { Pagination } from "@/components/Pagination";

describe("Pagination", () => {
  it("disables Previous on the first page", () => {
    render(<Pagination offset={0} limit={25} isLastPage={false} onChange={() => {}} />);
    expect(screen.getByRole("button", { name: /previous/i })).toBeDisabled();
    expect(screen.getByRole("button", { name: /next/i })).not.toBeDisabled();
  });

  it("disables Next when isLastPage is true", () => {
    render(<Pagination offset={50} limit={25} isLastPage onChange={() => {}} />);
    expect(screen.getByRole("button", { name: /next/i })).toBeDisabled();
  });

  it("calls onChange with the next offset when Next is clicked", async () => {
    const onChange = vi.fn();
    render(<Pagination offset={25} limit={25} isLastPage={false} onChange={onChange} />);

    await userEvent.click(screen.getByRole("button", { name: /next/i }));

    expect(onChange).toHaveBeenCalledWith({ offset: 50, limit: 25 });
  });

  it("calls onChange with offset - limit when Previous is clicked", async () => {
    const onChange = vi.fn();
    render(<Pagination offset={50} limit={25} isLastPage={false} onChange={onChange} />);

    await userEvent.click(screen.getByRole("button", { name: /previous/i }));

    expect(onChange).toHaveBeenCalledWith({ offset: 25, limit: 25 });
  });
});
