# Artifacts

The PDF asks for artifacts that explain the thinking behind the solution. Drop them here as the work progresses. Suggested structure below — adapt freely.

> *"Please commit any artifacts that help us understand your thinking and approach. Examples might include: Planning or design notes, Architecture diagrams, Prompts or instructions used with AI tools, Trade-off explanations, Performance considerations."* — Salary Management Assessment

## Layout

```
artifacts/
├── README.md             <- you are here
├── planning/             <- design notes, decision logs (markdown)
│   └── .gitkeep
├── architecture/         <- diagrams (mermaid in .md, or PNG/SVG)
│   └── .gitkeep
├── prompts/              <- notable AI prompts and how they shaped the solution
│   └── .gitkeep
├── tradeoffs.md          <- explicit decisions: why FastAPI, why SQLite, why bulk_insert, why shadcn/ui, why Stitch MCP, ...
├── performance.md        <- seed benchmark, query plans, optimization log
└── demo/                 <- placeholder for the demo video link, GIFs, screenshots
    └── .gitkeep
```

## What goes where

| File / folder | What to record |
|---|---|
| `planning/` | Each major design step. Dated markdown notes. Sub-folders OK if it grows. |
| `architecture/` | Mermaid diagrams (`.md` files) and/or exported PNGs. Keep them small and focused. |
| `prompts/` | Prompts you sent the agent that mattered, including Stitch MCP prompts for generated screens. Pair each with the outcome and why it worked (or did not). |
| `tradeoffs.md` | Single file. One trade-off per heading. State the alternatives considered, what you picked, and why. |
| `performance.md` | Seed benchmark (10k rows time), insights endpoint latency, anything optimized. Include host/Python version when relevant. |
| `demo/` | The video link goes in `demo/README.md` (or just in the project root README). GIFs and screenshots live here. |

## Quick templates

### `tradeoffs.md` entry

```markdown
## Why FastAPI over Django/DRF

**Considered**: Django+DRF, FastAPI+SQLAlchemy, Flask, Node+Express.
**Picked**: FastAPI + SQLAlchemy 2 + Pydantic v2.
**Why**: lighter footprint for a small single-tenant app; Pydantic v2 doubles as request validation and response serialization; less boilerplate for ten endpoints.
**Cost**: less batteries-included than Django (auth, admin) — acceptable for the assessment scope.
```

### `performance.md` entry

```markdown
## 2026-MM-DD — Seed 10,000 employees

- Approach: `db.execute(insert(Employee), [dict, ...])`, single transaction.
- Host: macOS 14.5, M2, Python 3.12.
- Result: **2.84s** for 10,000 rows.
- Notes: tried `bulk_insert_mappings` (2.91s) and per-row `add` (12.4s). PRAGMA `journal_mode=WAL` did not help at this volume.
```

### `prompts/<name>.md` entry

```markdown
# Prompt: design the salary insights service

**Context**: needed to decide between ORM aggregation and raw SQL.
**Prompt**: "COUNCIL: ORM vs raw SQL for avg/min/max grouped by country on a 10k-row SQLite table."
**Outcome**: council recommended ORM; the resulting query is in `app/services/salary_insights_service.py:23`.
```

### `prompts/stitch-<screen>.md` entry

```markdown
# Stitch MCP: dashboard layout

**Context**: needed a responsive shell with sidebar navigation and a KPI strip.
**Prompt** (sent to the `stitch` MCP): "React 18 + TS + Tailwind + shadcn/ui dashboard shell — left sidebar (Employees, Insights, Dashboard), top bar with search, main area with 4 shadcn `Card` KPI tiles + Recharts `BarChart` placeholder. Responsive down to 768px."
**What was kept**: sidebar markup, card grid layout.
**What was rewritten**: removed inline color hex codes, swapped raw `<button>` for shadcn `Button`, added focus-ring classes for accessibility, split into `components/layout/AppShell.tsx` and `components/dashboard/KpiGrid.tsx`.
**Tests added before commit**: `AppShell.test.tsx` verifies the active route highlight; `KpiGrid.test.tsx` verifies values render when the query resolves.
```

## Demo video

The PDF requires a video demo. Put the link in `demo/README.md` and in the root `README.md`. A 2–3 minute walkthrough is enough: seed → list → create → insights.
