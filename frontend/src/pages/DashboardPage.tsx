import { AnalyticsSection } from "@/components/AnalyticsSection";
import { CountryDistributionChart } from "@/components/CountryDistributionChart";
import { InfoHint } from "@/components/InfoHint";
import { KpiCard } from "@/components/KpiCard";
import { SummaryList } from "@/components/SummaryList";
import {
  useCountryDistribution,
  useGlobalOverview,
  useRecentEmployees,
} from "@/hooks/useInsights";

const TOOLTIP_DISTRIBUTION =
  "Headcount distribution across countries. Useful for spotting concentration of risk or growth opportunities.";
const TOOLTIP_RECENT =
  "Most recently added employees. Useful for onboarding follow-ups and audit trails.";

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
          <KpiCard label="Average Salary" value={overview.data.average_salary} />
          <KpiCard label="Countries" value={String(overview.data.active_countries)} />
          <KpiCard label="Job Titles" value={String(overview.data.active_titles)} />
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <AnalyticsSection
          id="distribution"
          title="Employees by Country"
          tooltip={<InfoHint label="Employees by Country">{TOOLTIP_DISTRIBUTION}</InfoHint>}
        >
          {distribution.isLoading ? (
            <p role="status" className="text-sm text-slate-500">
              Loading…
            </p>
          ) : distribution.data ? (
            <CountryDistributionChart counts={distribution.data.counts} />
          ) : null}
        </AnalyticsSection>

        <AnalyticsSection
          id="recent"
          title="Recent Hires"
          tooltip={<InfoHint label="Recent Hires">{TOOLTIP_RECENT}</InfoHint>}
        >
          {recent.isLoading ? (
            <p role="status" className="text-sm text-slate-500">
              Loading…
            </p>
          ) : recent.data && recent.data.length > 0 ? (
            <SummaryList
              ariaLabel="Recent hires"
              items={recent.data.map((e) => ({
                key: String(e.id),
                label: e.full_name,
                value: `${e.job_title} · ${e.country}`,
              }))}
            />
          ) : (
            <p
              role="status"
              className="rounded-md border border-dashed border-slate-300 bg-slate-50 px-4 py-12 text-center text-sm text-slate-500"
            >
              No employees yet — run the seed script.
            </p>
          )}
        </AnalyticsSection>
      </div>
    </section>
  );
}
