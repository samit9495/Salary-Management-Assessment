import { useState } from "react";

import type { EmployeeListParams } from "@/services/types";

type Props = {
  initial?: EmployeeListParams;
  onApply: (next: EmployeeListParams) => void;
};

export function EmployeesFilters({ initial = {}, onApply }: Props) {
  const [q, setQ] = useState(initial.q ?? "");
  const [country, setCountry] = useState(initial.country ?? "");
  const [sort, setSort] = useState(initial.sort ?? "");

  return (
    <form
      role="search"
      aria-label="Filter employees"
      className="flex flex-wrap items-end gap-3 rounded-md border border-slate-200 bg-white p-3"
      onSubmit={(e) => {
        e.preventDefault();
        onApply({
          q: q || undefined,
          country: country ? country.toUpperCase() : undefined,
          sort: sort || undefined,
        });
      }}
    >
      <label className="space-y-1 text-sm">
        <span className="font-medium text-slate-700">Search name</span>
        <input
          className="form-input"
          placeholder="Jane"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
      </label>
      <label className="space-y-1 text-sm">
        <span className="font-medium text-slate-700">Country</span>
        <input
          className="form-input w-24 uppercase"
          maxLength={2}
          placeholder="IN"
          value={country}
          onChange={(e) => setCountry(e.target.value)}
        />
      </label>
      <label className="space-y-1 text-sm">
        <span className="font-medium text-slate-700">Sort</span>
        <select
          className="form-input w-40"
          value={sort}
          onChange={(e) => setSort(e.target.value)}
        >
          <option value="">Default</option>
          <option value="full_name">Name A→Z</option>
          <option value="-full_name">Name Z→A</option>
          <option value="salary">Salary asc</option>
          <option value="-salary">Salary desc</option>
        </select>
      </label>
      <button
        type="submit"
        className="rounded-md bg-slate-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-800"
      >
        Apply
      </button>
    </form>
  );
}
