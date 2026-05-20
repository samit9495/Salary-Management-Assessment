# Artifacts

The PDF asks for artifacts that explain the thinking behind the solution.
All of the curated planning, architecture, decisions, and performance
work has been consolidated under [planning/](planning/) — start
[there](planning/README.md) for the reviewer-facing reading order.

> *"Please commit any artifacts that help us understand your thinking and approach. Examples might include: Planning or design notes, Architecture diagrams, Prompts or instructions used with AI tools, Trade-off explanations, Performance considerations."* — Salary Management Assessment

## Layout

```
artifacts/
├── README.md             <- you are here (layout map)
├── planning/             <- SINGLE curated planning surface (start here)
│   ├── README.md
│   ├── roadmap.md
│   ├── implementation-phases.md
│   ├── backend-architecture.md
│   ├── frontend-architecture.md
│   ├── analytics-strategy.md
│   ├── seed-performance-strategy.md
│   ├── testing-strategy.md
│   ├── ui-ux-decisions.md
│   ├── ai-assisted-workflow.md
│   ├── scalability-considerations.md
│   └── tradeoffs-and-decisions.md
├── architecture/         <- shim → planning/backend-architecture.md + frontend-architecture.md
├── tradeoffs.md          <- shim → planning/tradeoffs-and-decisions.md
├── performance.md        <- shim → planning/seed-performance-strategy.md
├── prompts/              <- driving prompts + Stitch / LLM Council catalog
└── demo/                 <- demo video link + screenshots
```

## What goes where

| Location | What to read |
|---|---|
| [planning/](planning/) | **Single curated planning surface.** Start at [planning/README.md](planning/README.md) for the index. |
| [prompts/](prompts/) | High-signal driving prompts (verbatim) plus Stitch MCP and LLM Council prompts paired with outcomes. |
| [architecture/](architecture/) | Shim — redirects to [planning/backend-architecture.md](planning/backend-architecture.md) + [planning/frontend-architecture.md](planning/frontend-architecture.md). |
| [tradeoffs.md](tradeoffs.md) | Shim — redirects to [planning/tradeoffs-and-decisions.md](planning/tradeoffs-and-decisions.md). |
| [performance.md](performance.md) | Shim — redirects to [planning/seed-performance-strategy.md](planning/seed-performance-strategy.md). |
| [demo/](demo/) | Demo video link in `demo/README.md` (or root `README.md`); screenshots / GIFs alongside. |

## Companion locations (outside artifacts/)

- [`../.cursor/plans/`](../.cursor/plans/) — raw, AI-generated planning files (audit trail; preserved verbatim).
- [`../tasks/`](../tasks/) — working notes (`todo.md`, `lessons.md`, `manual-test-scenarios.md`).
- [`../.cursor/rules/`](../.cursor/rules/) — always-apply engineering policy referenced from the planning docs.

## Adding new artifacts

When a new decision lands:

1. Add the trade-off to [planning/tradeoffs-and-decisions.md](planning/tradeoffs-and-decisions.md) under the right category.
2. Update the relevant per-concern document (e.g. [planning/backend-architecture.md](planning/backend-architecture.md), [planning/analytics-strategy.md](planning/analytics-strategy.md)).
3. If it's a performance number, append a dated entry to [planning/seed-performance-strategy.md](planning/seed-performance-strategy.md).
4. If it's an AI workflow change, append to [planning/ai-assisted-workflow.md](planning/ai-assisted-workflow.md).

Every reusable template (trade-off entry, performance entry, Stitch
prompt format) lives in the destination doc itself, so the example
sits next to the real entries.

## Demo video

The PDF requires a video demo. Put the link in `demo/README.md` and in the root `README.md`. A 2–3 minute walkthrough is enough: seed → list → create → insights.
