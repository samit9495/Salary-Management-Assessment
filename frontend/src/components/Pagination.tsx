type Props = {
  offset: number;
  limit: number;
  isLastPage: boolean;
  onChange: (next: { offset: number; limit: number }) => void;
};

export function Pagination({ offset, limit, isLastPage, onChange }: Props) {
  const start = offset + 1;
  const end = offset + limit;

  return (
    <div className="flex items-center justify-between text-sm text-slate-600">
      <span>
        Showing {start}–{end}
      </span>
      <div className="flex items-center gap-2">
        <button
          type="button"
          className="rounded-md border border-slate-300 px-3 py-1 text-sm hover:bg-slate-100 disabled:opacity-40"
          disabled={offset === 0}
          onClick={() => onChange({ offset: Math.max(0, offset - limit), limit })}
        >
          Previous
        </button>
        <button
          type="button"
          className="rounded-md border border-slate-300 px-3 py-1 text-sm hover:bg-slate-100 disabled:opacity-40"
          disabled={isLastPage}
          onClick={() => onChange({ offset: offset + limit, limit })}
        >
          Next
        </button>
      </div>
    </div>
  );
}
