import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { CompaRatioBadge, compaRatioBucket } from "@/components/CompaRatioBadge";

describe("compaRatioBucket", () => {
  it.each([
    [0.5, "underpaid"],
    [0.79, "underpaid"],
    [0.8, "healthy"],
    [1.0, "healthy"],
    [1.19, "healthy"],
    [1.2, "highly_compensated"],
    [1.5, "highly_compensated"],
  ])("%s → %s", (ratio, expected) => {
    expect(compaRatioBucket(ratio)).toBe(expected);
  });
});

describe("CompaRatioBadge", () => {
  it("renders the ratio as a percentage with a descriptive aria-label", () => {
    render(<CompaRatioBadge ratio={0.75} />);

    const badge = screen.getByRole("status", { name: /compa-ratio/i });
    expect(badge).toHaveTextContent("75%");
    expect(badge).toHaveAttribute("aria-label", expect.stringMatching(/underpaid/i));
  });

  it("uses red styling when underpaid", () => {
    render(<CompaRatioBadge ratio={0.5} />);
    expect(screen.getByRole("status")).toHaveClass(/bg-red-/);
  });

  it("uses green styling when healthy", () => {
    render(<CompaRatioBadge ratio={1.0} />);
    expect(screen.getByRole("status")).toHaveClass(/bg-emerald-/);
  });

  it("uses orange styling when highly compensated", () => {
    render(<CompaRatioBadge ratio={1.3} />);
    expect(screen.getByRole("status")).toHaveClass(/bg-amber-/);
  });
});
