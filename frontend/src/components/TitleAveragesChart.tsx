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
  averages: Record<string, string>;
};

export function TitleAveragesChart({ averages }: Props) {
  const data = Object.entries(averages).map(([title, value]) => ({
    title,
    average: Number(value),
  }));

  if (data.length === 0) {
    return (
      <p
        role="status"
        className="rounded-md border border-dashed border-slate-300 bg-slate-50 px-4 py-12 text-center text-sm text-slate-500"
      >
        No salary data for this country.
      </p>
    );
  }

  return (
    <div
      role="img"
      aria-label="Average salary by job title"
      className="h-72 w-full rounded-md border border-slate-200 bg-white p-4"
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="title" tick={{ fontSize: 12 }} interval={0} angle={-20} textAnchor="end" height={60} />
          <YAxis tickFormatter={(v: number) => v.toLocaleString()} />
          <Tooltip formatter={(v) => Number(v ?? 0).toLocaleString()} />
          <Bar dataKey="average" fill="#0f172a" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
