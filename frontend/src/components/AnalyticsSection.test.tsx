import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AnalyticsSection } from "@/components/AnalyticsSection";
import { InfoHint } from "@/components/InfoHint";
import { TooltipProvider } from "@/components/ui/tooltip";

function renderSection(node: React.ReactNode) {
  return render(<TooltipProvider delayDuration={0}>{node}</TooltipProvider>);
}

describe("AnalyticsSection", () => {
  it("renders the title as an h2 with the children below", () => {
    renderSection(
      <AnalyticsSection title="Total Compensation Burden">
        <p>chart goes here</p>
      </AnalyticsSection>,
    );

    expect(
      screen.getByRole("heading", { level: 2, name: /total compensation burden/i }),
    ).toBeInTheDocument();
    expect(screen.getByText("chart goes here")).toBeInTheDocument();
  });

  it("renders an optional description below the title", () => {
    renderSection(
      <AnalyticsSection
        title="Compensation Outliers"
        description="Bottom and top 5% within each peer group."
      >
        <p>content</p>
      </AnalyticsSection>,
    );

    expect(
      screen.getByText(/bottom and top 5%/i),
    ).toBeInTheDocument();
  });

  it("renders an InfoHint beside the title when tooltip is provided", () => {
    renderSection(
      <AnalyticsSection
        title="Average Salary by Job Title"
        tooltip={<InfoHint label="Average Salary by Job Title">Per-role mean.</InfoHint>}
      >
        <p>content</p>
      </AnalyticsSection>,
    );

    expect(
      screen.getByRole("button", { name: /average salary by job title/i }),
    ).toBeInTheDocument();
  });

  it("renders an actions slot on the right of the header", () => {
    renderSection(
      <AnalyticsSection
        title="Country Overview"
        actions={<button type="button">Filter</button>}
      >
        <p>content</p>
      </AnalyticsSection>,
    );

    expect(screen.getByRole("button", { name: /filter/i })).toBeInTheDocument();
  });

  it("uses aria-labelledby when a stable id is provided", () => {
    renderSection(
      <AnalyticsSection title="Recent Hires" id="recent-hires">
        <p>content</p>
      </AnalyticsSection>,
    );

    const heading = screen.getByRole("heading", { level: 2, name: /recent hires/i });
    expect(heading).toHaveAttribute("id", "recent-hires-title");
    const section = heading.closest("section");
    expect(section).toHaveAttribute("aria-labelledby", "recent-hires-title");
  });
});
