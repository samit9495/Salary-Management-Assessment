import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { TooltipProvider } from "@/components/ui/tooltip";
import { EmployeesPage } from "@/pages/EmployeesPage";
import { employeesApi } from "@/services/employees";
import type { Employee } from "@/services/types";

vi.mock("@/services/employees", () => ({
  employeesApi: {
    list: vi.fn(),
    get: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
    countries: vi.fn(),
    compensationAnalysis: vi.fn(),
  },
}));

const apiMock = employeesApi as unknown as {
  list: ReturnType<typeof vi.fn>;
  create: ReturnType<typeof vi.fn>;
  update: ReturnType<typeof vi.fn>;
  remove: ReturnType<typeof vi.fn>;
  countries: ReturnType<typeof vi.fn>;
  compensationAnalysis: ReturnType<typeof vi.fn>;
};

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <TooltipProvider delayDuration={0}>
        <EmployeesPage />
      </TooltipProvider>
    </QueryClientProvider>,
  );
}

const employee = (id: number, name: string): Employee => ({
  id,
  full_name: name,
  job_title: "Engineer",
  country: "IN",
  salary: "50000.00",
  email: null,
  department: null,
  hire_date: null,
  is_active: true,
});

beforeEach(() => {
  apiMock.list.mockReset();
  apiMock.create.mockReset();
  apiMock.update.mockReset();
  apiMock.remove.mockReset();
  apiMock.countries.mockReset();
  apiMock.countries.mockResolvedValue({ countries: [] });
  apiMock.compensationAnalysis.mockReset();
  apiMock.compensationAnalysis.mockResolvedValue({ analyses: [] });
});

describe("EmployeesPage", () => {
  it("loads and renders employees from the API", async () => {
    apiMock.list.mockResolvedValue({
      rows: [employee(1, "Jane Doe"), employee(2, "John Smith")],
      total: 2,
    });

    renderPage();

    expect(await screen.findByText("Jane Doe")).toBeInTheDocument();
    expect(screen.getByText("John Smith")).toBeInTheDocument();
    expect(apiMock.list).toHaveBeenCalled();
  });

  it("renders compa-ratio badges when compensation analysis is available", async () => {
    apiMock.list.mockResolvedValue({
      rows: [employee(1, "Jane Doe"), employee(2, "John Smith")],
      total: 2,
    });
    apiMock.compensationAnalysis.mockResolvedValue({
      analyses: [
        {
          id: 1,
          peer_avg: "100.00",
          peer_min: "50.00",
          peer_max: "150.00",
          compa_ratio: "0.7500",
          range_penetration: "0.2000",
        },
        {
          id: 2,
          peer_avg: "100.00",
          peer_min: "50.00",
          peer_max: "150.00",
          compa_ratio: "1.3000",
          range_penetration: "0.9000",
        },
      ],
    });

    renderPage();

    expect(await screen.findByText("75%")).toBeInTheDocument();
    expect(screen.getByText("130%")).toBeInTheDocument();
  });

  it("shows info tooltips beside the Compa and Spread column headers", async () => {
    apiMock.list.mockResolvedValue({
      rows: [employee(1, "Jane Doe")],
      total: 1,
    });
    apiMock.compensationAnalysis.mockResolvedValue({
      analyses: [
        {
          id: 1,
          peer_avg: "100.00",
          peer_min: "50.00",
          peer_max: "150.00",
          compa_ratio: "1.0000",
          range_penetration: "0.5000",
        },
      ],
    });

    renderPage();

    await screen.findByText("Jane Doe");
    expect(
      await screen.findByRole("button", { name: /^compa$/i }),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole("button", { name: /^spread$/i }),
    ).toBeInTheDocument();
  });

  it("renders the 'of N' pagination summary using the API total", async () => {
    apiMock.list.mockResolvedValue({
      rows: [employee(1, "Jane Doe"), employee(2, "John Smith")],
      total: 137,
    });

    renderPage();

    await screen.findByText("Jane Doe");
    expect(screen.getByText(/showing 1\u201325 of 137/i)).toBeInTheDocument();
  });

  it("opens the create form and posts a new employee", async () => {
    apiMock.list.mockResolvedValue({ rows: [], total: 0 });
    apiMock.create.mockResolvedValue(employee(7, "Alice Roe"));

    renderPage();

    await userEvent.click(await screen.findByRole("button", { name: /new employee/i }));
    const form = within(screen.getByRole("form", { name: /employee form/i }));
    await userEvent.type(form.getByLabelText(/full name/i), "Alice Roe");
    await userEvent.type(form.getByLabelText(/job title/i), "Designer");
    await userEvent.type(form.getByLabelText(/country/i), "us");
    await userEvent.type(form.getByLabelText(/salary/i), "60000");
    await userEvent.click(form.getByRole("button", { name: /^create$/i }));

    await waitFor(() => expect(apiMock.create).toHaveBeenCalledTimes(1));
    expect(apiMock.create.mock.calls[0]![0]).toMatchObject({
      full_name: "Alice Roe",
      country: "US",
      salary: "60000",
    });
  });
});
