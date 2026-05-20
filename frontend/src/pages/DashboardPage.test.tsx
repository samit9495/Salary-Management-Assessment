import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { TooltipProvider } from "@/components/ui/tooltip";
import { DashboardPage } from "@/pages/DashboardPage";
import { insightsApi } from "@/services/insights";

vi.mock("@/services/insights", () => ({
  insightsApi: {
    overview: vi.fn(),
    recent: vi.fn(),
    distribution: vi.fn(),
    byCountry: vi.fn(),
    byCountryAndTitle: vi.fn(),
    topTitles: vi.fn(),
  },
}));

const apiMock = insightsApi as unknown as {
  overview: ReturnType<typeof vi.fn>;
  recent: ReturnType<typeof vi.fn>;
  distribution: ReturnType<typeof vi.fn>;
};

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <TooltipProvider delayDuration={0}>
        <DashboardPage />
      </TooltipProvider>
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  apiMock.overview.mockReset();
  apiMock.recent.mockReset();
  apiMock.distribution.mockReset();
});

describe("DashboardPage", () => {
  it("renders the global overview KPIs from the API", async () => {
    apiMock.overview.mockResolvedValue({
      total_employees: 100,
      average_salary: "75000.00",
      active_countries: 5,
      active_titles: 12,
    });
    apiMock.recent.mockResolvedValue([]);
    apiMock.distribution.mockResolvedValue({ counts: {} });

    renderPage();

    expect(await screen.findByText("100")).toBeInTheDocument();
    expect(screen.getByText("75000.00")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
  });

  it("exposes info tooltips beside Employees by Country and Recent Hires", async () => {
    apiMock.overview.mockResolvedValue({
      total_employees: 1,
      average_salary: "1.00",
      active_countries: 1,
      active_titles: 1,
    });
    apiMock.recent.mockResolvedValue([]);
    apiMock.distribution.mockResolvedValue({ counts: { IN: 1 } });

    renderPage();

    expect(
      await screen.findByRole("button", { name: /employees by country/i }),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole("button", { name: /recent hires/i }),
    ).toBeInTheDocument();
  });

  it("renders recent hires when present", async () => {
    apiMock.overview.mockResolvedValue({
      total_employees: 1,
      average_salary: "1.00",
      active_countries: 1,
      active_titles: 1,
    });
    apiMock.recent.mockResolvedValue([
      {
        id: 5,
        full_name: "Recent Hire",
        job_title: "Engineer",
        country: "IN",
        salary: "1.00",
        email: null,
        department: null,
        hire_date: null,
        is_active: true,
      },
    ]);
    apiMock.distribution.mockResolvedValue({ counts: { IN: 1 } });

    renderPage();

    expect(await screen.findByText("Recent Hire")).toBeInTheDocument();
  });
});
