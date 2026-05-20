import { cn } from "@/lib/utils";

type Props = {
  value: number;
  className?: string;
};

function clamp01(value: number): number {
  if (Number.isNaN(value) || value < 0) return 0;
  if (value > 1) return 1;
  return value;
}

export function RangePenetrationBar({ value, className }: Props) {
  const clamped = clamp01(value);
  const pct = Math.round(clamped * 100);
  return (
    <div className={cn("flex w-32 items-center gap-2", className)}>
      <div
        role="progressbar"
        aria-label={`Range penetration ${pct}%`}
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        className="relative h-2 flex-1 overflow-hidden rounded-full bg-slate-200"
      >
        <div
          className="absolute inset-y-0 left-0 rounded-full bg-slate-600"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="w-9 text-right text-xs tabular-nums text-slate-600">
        {pct}%
      </span>
    </div>
  );
}
