import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { TooltipProvider } from "@/components/ui/tooltip";
import { InsightsPage } from "@/pages/InsightsPage";
import { employeesApi } from "@/services/employees";
import { insightsApi } from "@/services/insights";

vi.mock("@/services/insights", () => ({
  insightsApi: {
    byCountry: vi.fn(),
    byCountryAndTitle: vi.fn(),
    topTitles: vi.fn(),
    payrollByCountry: vi.fn(),
    payrollByTitle: vi.fn(),
    outliers: vi.fn(),
  },
}));

vi.mock("@/services/employees", () => ({
  employeesApi: {
    countries: vi.fn(),
  },
}));

const apiMock = insightsApi as unknown as {
  byCountry: ReturnType<typeof vi.fn>;
  byCountryAndTitle: ReturnType<typeof vi.fn>;
  payrollByCountry: ReturnType<typeof vi.fn>;
  payrollByTitle: ReturnType<typeof vi.fn>;
  outliers: ReturnType<typeof vi.fn>;
};

const employeesMock = employeesApi as unknown as {
  countries: ReturnType<typeof vi.fn>;
};

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <TooltipProvider delayDuration={0}>
        <InsightsPage />
      </TooltipProvider>
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  apiMock.byCountry.mockReset();
  apiMock.byCountryAndTitle.mockReset();
  apiMock.payrollByCountry.mockReset();
  apiMock.payrollByTitle.mockReset();
  apiMock.payrollByCountry.mockResolvedValue({ total: "0.00", entries: [] });
  apiMock.payrollByTitle.mockResolvedValue({ total: "0.00", entries: [] });
  apiMock.outliers.mockReset();
  apiMock.outliers.mockResolvedValue({ bucket: "bottom", entries: [] });
  employeesMock.countries.mockReset();
  employeesMock.countries.mockResolvedValue({
    countries: [{ code: "IN", count: 1 }],
  });
});

describe("InsightsPage", () => {
  it("renders compensation outlier tables for top and bottom buckets", async () => {
    apiMock.byCountry.mockResolvedValue({
      country: "IN",
      average_salary: "100000.00",
      min_salary: "30000.00",
      max_salary: "250000.00",
      employee_count: 1,
    });
    apiMock.byCountryAndTitle.mockResolvedValue({ country: "IN", averages: {} });
    apiMock.outliers.mockImplementation((bucket: string) =>
      Promise.resolve({
        bucket,
        entries: [
          {
            id: bucket === "bottom" ? 1 : 99,
            full_name: bucket === "bottom" ? "Junior Joe" : "Senior Sam",
            country: "IN",
            job_title: "Engineer",
            salary: bucket === "bottom" ? "10.00" : "200.00",
            bucket: bucket === "bottom" ? 1 : 20,
          },
        ],
      }),
    );

    renderPage();

    expect(
      await screen.findByRole("heading", { name: /bottom 5%/i }),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole("heading", { name: /top 5%/i }),
    ).toBeInTheDocument();
    expect(await screen.findByText("Junior Joe")).toBeInTheDocument();
    expect(await screen.findByText("Senior Sam")).toBeInTheDocument();
  });

  it("renders the payroll breakdown sections", async () => {
    apiMock.byCountry.mockResolvedValue({
      country: "IN",
      average_salary: "100000.00",
      min_salary: "30000.00",
      max_salary: "250000.00",
      employee_count: 1,
    });
    apiMock.byCountryAndTitle.mockResolvedValue({ country: "IN", averages: {} });
    apiMock.payrollByCountry.mockResolvedValue({
      total: "1000.00",
      entries: [
        { key: "IN", total: "700.00", percentage: "70.00" },
        { key: "US", total: "300.00", percentage: "30.00" },
      ],
    });
    apiMock.payrollByTitle.mockResolvedValue({ total: "0.00", entries: [] });

    renderPage();

    expect(
      await screen.findByRole("heading", { name: /total compensation burden/i }),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole("img", { name: /by country/i }),
    ).toBeInTheDocument();
  });

  it("renders the payroll entries as a bordered SummaryList with per-row total and percentage", async () => {
    apiMock.byCountry.mockResolvedValue({
      country: "IN",
      average_salary: "100000.00",
      min_salary: "30000.00",
      max_salary: "250000.00",
      employee_count: 1,
    });
    apiMock.byCountryAndTitle.mockResolvedValue({ country: "IN", averages: {} });
    apiMock.payrollByCountry.mockResolvedValue({
      total: "1000.00",
      entries: [
        { key: "IN", total: "700.00", percentage: "70.00" },
        { key: "US", total: "300.00", percentage: "30.00" },
      ],
    });
    apiMock.payrollByTitle.mockResolvedValue({ total: "0.00", entries: [] });

    renderPage();

    const list = await screen.findByRole("list", { name: /by country breakdown/i });
    const rows = within(list).getAllByRole("listitem");
    expect(rows).toHaveLength(2);
    expect(within(rows[0]!).getByText("IN")).toBeInTheDocument();
    expect(within(rows[0]!).getByText("700")).toBeInTheDocument();
    expect(within(rows[0]!).getByText("70.00%")).toBeInTheDocument();
  });

  it("exposes info tooltips beside the advanced analytics sections", async () => {
    apiMock.byCountry.mockResolvedValue({
      country: "IN",
      average_salary: "100000.00",
      min_salary: "30000.00",
      max_salary: "250000.00",
      employee_count: 1,
    });
    apiMock.byCountryAndTitle.mockResolvedValue({ country: "IN", averages: {} });

    renderPage();

    expect(
      await screen.findByRole("button", { name: /average salary by job title/i }),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole("button", { name: /total compensation burden/i }),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole("button", { name: /compensation outliers/i }),
    ).toBeInTheDocument();
  });

  it("stacks payroll breakdown vertically with Job Title first then Country", async () => {
    apiMock.byCountry.mockResolvedValue({
      country: "IN",
      average_salary: "100000.00",
      min_salary: "30000.00",
      max_salary: "250000.00",
      employee_count: 1,
    });
    apiMock.byCountryAndTitle.mockResolvedValue({ country: "IN", averages: {} });
    apiMock.payrollByCountry.mockResolvedValue({
      total: "0.00",
      entries: [],
    });
    apiMock.payrollByTitle.mockResolvedValue({
      total: "0.00",
      entries: [],
    });

    renderPage();

    const titleHeading = await screen.findByRole("heading", {
      name: /^by job title$/i,
    });
    const countryHeading = await screen.findByRole("heading", {
      name: /^by country$/i,
    });

    expect(
      titleHeading.compareDocumentPosition(countryHeading) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
  });

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
