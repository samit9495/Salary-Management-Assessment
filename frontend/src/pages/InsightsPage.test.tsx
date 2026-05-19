import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { InsightsPage } from "@/pages/InsightsPage";
import { insightsApi } from "@/services/insights";

vi.mock("@/services/insights", () => ({
  insightsApi: {
    byCountry: vi.fn(),
    byCountryAndTitle: vi.fn(),
    topTitles: vi.fn(),
  },
}));

const apiMock = insightsApi as unknown as {
  byCountry: ReturnType<typeof vi.fn>;
  byCountryAndTitle: ReturnType<typeof vi.fn>;
};

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <InsightsPage />
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  apiMock.byCountry.mockReset();
  apiMock.byCountryAndTitle.mockReset();
});

describe("InsightsPage", () => {
  it("renders KPI cards for the default country", async () => {
    apiMock.byCountry.mockResolvedValue({
      country: "IN",
      average_salary: "100000.00",
      min_salary: "30000.00",
      max_salary: "250000.00",
      employee_count: 1234,
    });
    apiMock.byCountryAndTitle.mockResolvedValue({ country: "IN", averages: {} });

    renderPage();

    expect(await screen.findByText("1234")).toBeInTheDocument();
    expect(screen.getByText("100000.00")).toBeInTheDocument();
    expect(screen.getByText("30000.00")).toBeInTheDocument();
    expect(screen.getByText("250000.00")).toBeInTheDocument();
  });
});
