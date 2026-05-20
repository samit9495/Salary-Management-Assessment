import { type ReactNode } from "react";

import { CompaRatioBadge } from "@/components/CompaRatioBadge";
import { InfoHint } from "@/components/InfoHint";
import { RangePenetrationBar } from "@/components/RangePenetrationBar";
import type {
  Employee,
  EmployeeCompensationAnalysis,
} from "@/services/types";

type Props = {
  employees: Employee[];
  analyses?: Record<number, EmployeeCompensationAnalysis>;
  onEdit?: (employee: Employee) => void;
  onDelete?: (employee: Employee) => void;
};

type Column = { key: string; header: ReactNode };

const BASE_COLUMNS: Column[] = [
  { key: "Name", header: "Name" },
  { key: "Title", header: "Title" },
  { key: "Country", header: "Country" },
  { key: "Salary", header: "Salary" },
  { key: "Department", header: "Department" },
  { key: "Active", header: "Active" },
];

const TOOLTIP_COMPA =
  "Compa-ratio: salary ÷ peer-group average. Below 80% may indicate underpayment risk; above 120% may need budget review.";
const TOOLTIP_SPREAD =
  "Range penetration: where the salary sits between peer-group min and max. 0% = floor, 100% = ceiling.";

const ANALYTICS_COLUMNS: Column[] = [
  {
    key: "Compa",
    header: (
      <span className="inline-flex items-center gap-1">
        Compa
        <InfoHint label="Compa">{TOOLTIP_COMPA}</InfoHint>
      </span>
    ),
  },
  {
    key: "Spread",
    header: (
      <span className="inline-flex items-center gap-1">
        Spread
        <InfoHint label="Spread">{TOOLTIP_SPREAD}</InfoHint>
      </span>
    ),
  },
];

const ACTIONS_COLUMN: Column = { key: "Actions", header: "" };

export function EmployeesTable({ employees, analyses, onEdit, onDelete }: Props) {
  if (employees.length === 0) {
    return (
      <p
        role="status"
        className="rounded-md border border-dashed border-slate-300 bg-slate-50 px-4 py-12 text-center text-sm text-slate-500"
      >
        No employees match your filters.
      </p>
    );
  }

  const showAnalytics = analyses !== undefined;
  const columns: Column[] = showAnalytics
    ? [...BASE_COLUMNS, ...ANALYTICS_COLUMNS, ACTIONS_COLUMN]
    : [...BASE_COLUMNS, ACTIONS_COLUMN];

  return (
    <div className="overflow-hidden rounded-md border border-slate-200">
      <table className="w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-100 text-left text-xs uppercase tracking-wide text-slate-600">
          <tr>
            {columns.map((col) => (
              <th key={col.key} scope="col" className="px-3 py-2 font-medium">
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white">
          {employees.map((e) => {
            const analysis = analyses?.[e.id];
            return (
              <tr key={e.id} className="hover:bg-slate-50">
                <td className="px-3 py-2 font-medium text-slate-900">{e.full_name}</td>
                <td className="px-3 py-2 text-slate-700">{e.job_title}</td>
                <td className="px-3 py-2 text-slate-700">{e.country}</td>
                <td className="px-3 py-2 text-right tabular-nums text-slate-700">
                  {e.salary}
                </td>
                <td className="px-3 py-2 text-slate-700">{e.department ?? "—"}</td>
                <td className="px-3 py-2 text-slate-700">{e.is_active ? "Yes" : "No"}</td>
                {showAnalytics && (
                  <td className="px-3 py-2">
                    {analysis ? (
                      <CompaRatioBadge ratio={Number(analysis.compa_ratio)} />
                    ) : (
                      <span className="text-xs text-slate-400">—</span>
                    )}
                  </td>
                )}
                {showAnalytics && (
                  <td className="px-3 py-2">
                    {analysis ? (
                      <RangePenetrationBar value={Number(analysis.range_penetration)} />
                    ) : (
                      <span className="text-xs text-slate-400">—</span>
                    )}
                  </td>
                )}
                <td className="px-3 py-2 text-right">
                  <div className="flex justify-end gap-2">
                    {onEdit && (
                      <button
                        type="button"
                        className="rounded border border-slate-300 px-2 py-1 text-xs text-slate-700 hover:bg-slate-100"
                        onClick={() => onEdit(e)}
                      >
                        Edit
                      </button>
                    )}
                    {onDelete && (
                      <button
                        type="button"
                        className="rounded border border-red-200 px-2 py-1 text-xs text-red-700 hover:bg-red-50"
                        onClick={() => onDelete(e)}
                      >
                        Delete
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
