import { CountryDistributionChart } from "@/components/CountryDistributionChart";
import { KpiCard } from "@/components/KpiCard";
import {
  useCountryDistribution,
  useGlobalOverview,
  useRecentEmployees,
} from "@/hooks/useInsights";

export function DashboardPage() {
  const overview = useGlobalOverview();
  const recent = useRecentEmployees(5);
  const distribution = useCountryDistribution();

  return (
    <section aria-labelledby="dashboard-heading" className="space-y-6">
      <header>
        <h1 id="dashboard-heading" className="text-2xl font-semibold text-slate-900">
          Dashboard
        </h1>
        <p className="text-sm text-slate-600">
          Salary insights at a glance for the whole organization.
        </p>
      </header>

      {overview.isLoading ? (
        <p role="status" className="text-sm text-slate-500">
          Loading overview…
        </p>
      ) : overview.isError ? (
        <p role="alert" className="text-sm text-red-700">
          Failed to load overview.
        </p>
      ) : overview.data ? (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard label="Employees" value={String(overview.data.total_employees)} />
          <KpiCard label="Average salary" value={overview.data.average_salary} />
          <KpiCard label="Countries" value={String(overview.data.active_countries)} />
          <KpiCard label="Job titles" value={String(overview.data.active_titles)} />
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section aria-labelledby="distribution-heading">
          <h2 id="distribution-heading" className="mb-2 text-lg font-semibold text-slate-800">
            Employees by country
          </h2>
          {distribution.isLoading ? (
            <p role="status" className="text-sm text-slate-500">
              Loading…
            </p>
          ) : distribution.data ? (
            <CountryDistributionChart counts={distribution.data.counts} />
          ) : null}
        </section>

        <section aria-labelledby="recent-heading">
          <h2 id="recent-heading" className="mb-2 text-lg font-semibold text-slate-800">
            Recent hires
          </h2>
          {recent.isLoading ? (
            <p role="status" className="text-sm text-slate-500">
              Loading…
            </p>
          ) : recent.data && recent.data.length > 0 ? (
            <ul className="divide-y divide-slate-200 overflow-hidden rounded-md border border-slate-200 bg-white">
              {recent.data.map((e) => (
                <li
                  key={e.id}
                  className="flex items-center justify-between px-3 py-2 text-sm"
                >
                  <span className="font-medium text-slate-900">{e.full_name}</span>
                  <span className="text-slate-600">
                    {e.job_title} · {e.country}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p
              role="status"
              className="rounded-md border border-dashed border-slate-300 bg-slate-50 px-4 py-12 text-center text-sm text-slate-500"
            >
              No employees yet — run the seed script.
            </p>
          )}
        </section>
      </div>
    </section>
  );
}
