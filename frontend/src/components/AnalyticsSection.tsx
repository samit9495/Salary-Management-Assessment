import { type ReactNode } from "react";

import { cn } from "@/lib/utils";

type Props = {
  title: string;
  description?: ReactNode;
  tooltip?: ReactNode;
  actions?: ReactNode;
  id?: string;
  children: ReactNode;
  className?: string;
  bodyClassName?: string;
};

export function AnalyticsSection({
  title,
  description,
  tooltip,
  actions,
  id,
  children,
  className,
  bodyClassName,
}: Props) {
  const headingId = id ? `${id}-title` : undefined;

  return (
    <section
      aria-labelledby={headingId}
      className={cn(
        "rounded-lg border border-slate-200 bg-white p-4 shadow-sm sm:p-6",
        className,
      )}
    >
      <header className="mb-3 flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-1.5">
            <h2
              id={headingId}
              className="text-lg font-semibold text-slate-900"
            >
              {title}
            </h2>
            {tooltip}
          </div>
          {description ? (
            <p className="mt-0.5 text-sm text-slate-500">{description}</p>
          ) : null}
        </div>
        {actions ? <div className="flex shrink-0 items-center gap-2">{actions}</div> : null}
      </header>
      <div className={cn("space-y-3", bodyClassName)}>{children}</div>
    </section>
  );
}
