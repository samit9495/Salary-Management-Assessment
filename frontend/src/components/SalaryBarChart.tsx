import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export type SalaryBarChartDatum = {
  key: string;
  value: number;
};

type Props = {
  data: SalaryBarChartDatum[];
  ariaLabel: string;
  emptyMessage?: string;
  height?: number;
  barColor?: string;
};

const ONE_MILLION = 1_000_000;
const ONE_THOUSAND = 1_000;

export function formatCompactCurrency(value: number): string {
  if (value === 0) return "0";
  if (Math.abs(value) >= ONE_MILLION) {
    return `${(value / ONE_MILLION).toFixed(1).replace(/\.0$/, "")}M`;
  }
  if (Math.abs(value) >= ONE_THOUSAND) {
    return `${Math.round(value / ONE_THOUSAND)}K`;
  }
  return String(value);
}

export function SalaryBarChart({
  data,
  ariaLabel,
  emptyMessage = "No data to display.",
  height = 288,
  barColor = "#0f172a",
}: Props) {
  if (data.length === 0) {
    return (
      <p
        role="status"
        aria-label={`No data for ${ariaLabel}`}
        className="rounded-md border border-dashed border-slate-300 bg-slate-50 px-4 py-12 text-center text-sm text-slate-500"
      >
        {emptyMessage}
      </p>
    );
  }

  return (
    <div
      role="img"
      aria-label={ariaLabel}
      style={{ height }}
      className="w-full rounded-md border border-slate-200 bg-white p-4"
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 8 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="key"
            tick={{ fontSize: 12 }}
            interval={0}
            angle={-20}
            textAnchor="end"
            height={60}
          />
          <YAxis
            width={80}
            tick={{ fontSize: 12 }}
            tickFormatter={formatCompactCurrency}
          />
          <Tooltip formatter={(v) => Number(v ?? 0).toLocaleString()} />
          <Bar dataKey="value" fill={barColor} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
