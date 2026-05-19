import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type Props = {
  counts: Record<string, number>;
};

export function CountryDistributionChart({ counts }: Props) {
  const data = Object.entries(counts)
    .map(([country, count]) => ({ country, count }))
    .sort((a, b) => b.count - a.count);

  if (data.length === 0) {
    return (
      <p
        role="status"
        className="rounded-md border border-dashed border-slate-300 bg-slate-50 px-4 py-12 text-center text-sm text-slate-500"
      >
        No country data yet.
      </p>
    );
  }

  return (
    <div
      role="img"
      aria-label="Employees by country"
      className="h-72 w-full rounded-md border border-slate-200 bg-white p-4"
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="country" tick={{ fontSize: 12 }} interval={0} />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Bar dataKey="count" fill="#0f172a" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
