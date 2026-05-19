import { useState } from "react";

import { KpiCard } from "@/components/KpiCard";
import { TitleAveragesChart } from "@/components/TitleAveragesChart";
import { useCountryInsights, useCountryTitleAverages } from "@/hooks/useInsights";

export function InsightsPage() {
  const [country, setCountry] = useState("IN");

  const summary = useCountryInsights(country);
  const breakdown = useCountryTitleAverages(country);

  return (
    <section aria-labelledby="insights-heading" className="space-y-4">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <h1 id="insights-heading" className="text-2xl font-semibold text-slate-900">
          Insights
        </h1>
        <label className="space-y-1 text-sm">
          <span className="font-medium text-slate-700">Country</span>
          <input
            className="form-input w-28 uppercase"
            maxLength={2}
            value={country}
            onChange={(e) => setCountry(e.target.value)}
          />
        </label>
      </header>

      {summary.isLoading ? (
        <p role="status" className="text-sm text-slate-500">
          Loading insights for {country}…
        </p>
      ) : summary.isError ? (
        <p role="alert" className="text-sm text-red-700">
          Failed to load insights.
        </p>
      ) : summary.data ? (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard label="Employees" value={String(summary.data.employee_count)} />
          <KpiCard label="Average" value={summary.data.average_salary} />
          <KpiCard label="Min" value={summary.data.min_salary} />
          <KpiCard label="Max" value={summary.data.max_salary} />
        </div>
      ) : null}

      <h2 className="pt-2 text-lg font-semibold text-slate-800">
        Average salary by job title
      </h2>
      {breakdown.isLoading ? (
        <p role="status" className="text-sm text-slate-500">
          Loading breakdown…
        </p>
      ) : breakdown.isError ? (
        <p role="alert" className="text-sm text-red-700">
          Failed to load breakdown.
        </p>
      ) : breakdown.data ? (
        <TitleAveragesChart averages={breakdown.data.averages} />
      ) : null}
    </section>
  );
}
