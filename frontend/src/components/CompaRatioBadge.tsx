import { cn } from "@/lib/utils";

export type CompaRatioBucket = "underpaid" | "healthy" | "highly_compensated";

const UNDERPAID_CEILING = 0.8;
const HEALTHY_CEILING = 1.2;

export function compaRatioBucket(ratio: number): CompaRatioBucket {
  if (ratio < UNDERPAID_CEILING) return "underpaid";
  if (ratio < HEALTHY_CEILING) return "healthy";
  return "highly_compensated";
}

const STYLE: Record<CompaRatioBucket, string> = {
  underpaid: "bg-red-100 text-red-700 ring-red-200",
  healthy: "bg-emerald-100 text-emerald-700 ring-emerald-200",
  highly_compensated: "bg-amber-100 text-amber-700 ring-amber-200",
};

const LABEL: Record<CompaRatioBucket, string> = {
  underpaid: "Underpaid",
  healthy: "Healthy",
  highly_compensated: "Highly compensated",
};

const TITLE: Record<CompaRatioBucket, string> = {
  underpaid: "Below 80% of the peer-group average — potential retention risk.",
  healthy: "Between 80% and 120% of the peer-group average.",
  highly_compensated: "Above 120% of the peer-group average — budget review.",
};

type Props = {
  ratio: number;
  className?: string;
};

export function CompaRatioBadge({ ratio, className }: Props) {
  const bucket = compaRatioBucket(ratio);
  const percentage = `${Math.round(ratio * 100)}%`;
  return (
    <span
      role="status"
      title={TITLE[bucket]}
      aria-label={`Compa-ratio ${percentage}, ${LABEL[bucket]}`}
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset",
        STYLE[bucket],
        className,
      )}
    >
      {percentage}
    </span>
  );
}
