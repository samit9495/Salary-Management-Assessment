# Salary-Management-Assessment — Agent Brief

> Read this file at the start of every session. It is the shortest possible orientation.

## What this project is

A minimal but production-quality salary management tool for an HR manager of an organization with 10,000 employees. Built as an Incubyte assessment that is graded on:

1. **Visible TDD evolution** in `git log` (Red → Green → Refactor commits).
2. **Software craftsmanship** values: SOLID, Clean Code, Simple Design.
3. **End-to-end working software**: backend + UI + seed + tests + deployed demo.

See `Salary Management Assessment.pdf` at the repo root for the full brief.

## Stack

| Layer | Choice |
|-------|--------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2.x, Pydantic v2 |
| Database | SQLite (single file, single tenant) |
| Frontend | React 18 + Vite + TypeScript (strict), Tailwind CSS, shadcn/ui, TanStack Query, TanStack Table, Recharts |
| Tests | pytest + httpx TestClient on backend; Vitest + RTL on frontend |
| Seed | 10,000 employees from `first_names.txt` + `last_names.txt`; bulk insert; deterministic via `--seed` |
| UI generation | Google Stitch MCP directly integrated for UI generation and React scaffolding |

## How to work in this repo

1. **Read `.cursor/rules/README.md`.** Always-apply rules first: TDD discipline, craftsmanship, commit hygiene.
2. **TDD is non-negotiable.** Use `.cursor/skills/incubyte-tdd-loop/SKILL.md` as your loop checklist.
3. **One TDD step = one commit.** Conventional Commits — `test:` / `feat:` / `fix:` / `refactor:`. See `.cursor/rules/incubyte-commit-hygiene.mdc`.
4. **Plan before doing.** Use Cursor's plan mode for any task > 3 steps. Track in `tasks/todo.md`.
5. **Log lessons** in `tasks/lessons.md`. Promote recurring lessons to `.cursor/rules/`.

## Agent roles

| Agent | When to use | File |
|-------|-------------|------|
| Code Reviewer | After a major feature; run the checklist including the git-log audit | `.cursor/agents/incubyte-code-reviewer.md` |
| QA Automation | When you need to validate coverage and produce manual test scenarios | `.cursor/agents/incubyte-qa-automation.md` |
| LLM Council | Genuine design tradeoffs only | `.cursor/skills/llm-council/SKILL.md` |

## Repo layout (target)

```
.
├── AGENTS.md                    <- you are here
├── README.md                    <- public setup/run/test docs
├── Salary Management Assessment.pdf
├── .cursor/                     <- rules, skills, agents
├── tasks/                       <- todo, lessons, manual test scenarios
├── artifacts/                   <- planning, architecture, prompts, trade-offs, perf, demo
├── app/                         <- FastAPI backend (Python)
├── tests/                       <- backend tests
├── frontend/                    <- React + Vite UI
├── scripts/                     <- seed and dev helpers
├── data/
│   ├── first_names.txt
│   └── last_names.txt
├── pyproject.toml
└── .gitignore
```

(See `.cursor/rules/incubyte-project-map.mdc` for the per-file responsibilities.)

## MCP servers used

### Project-level (`.cursor/mcp.json`)

- **`stitch`** — Google Stitch MCP for AI-assisted UI generation and React scaffolding. Primary UI workflow.

### User-level (already configured in Cursor)

- **`user-context7`** — primary docs lookup (FastAPI, SQLAlchemy, React, Vite, TanStack Query, shadcn/ui)
- **`user-github`** — repo / PR operations

### Stitch MCP configuration

The project-level `.cursor/mcp.json` declares the Stitch MCP:

```json
{
  "mcpServers": {
    "stitch": {
      "url": "https://stitch.googleapis.com/mcp",
      "headers": {
        "X-Goog-Api-Key": "API_KEY"
      }
    }
  }
}
```

Replace `API_KEY` with a real Google Stitch API key. Do **not** commit the key — set it via your local Cursor environment.

### How to use the Stitch MCP

Stitch is the project's primary UI generation workflow. Use it for:

- dashboard layouts
- forms (create / edit employee)
- analytics pages (charts, tables, country & job-title breakdowns)
- responsive scaffolding for the above

Developers remain responsible for:

- **Accessibility** — keyboard nav, ARIA labels, color contrast
- **Reusable components** — extract repeated UI into `components/`
- **State management** — TanStack Query for server state; local state via React
- **API integration** — typed fetchers in `src/services/`
- **Performance** — memoization where measurable, pagination on lists
- **Testing** — Vitest + React Testing Library, behavior over snapshots
- **Maintainability** — generated code is a *starting point*, not the final commit

### Rules for generated code

- Generated UI is **reviewed and refactored** before commit. Treat it like a draft from a junior pair.
- Do **not** blindly commit Stitch output. Split it into small TDD commits: one for the failing component test, one for the implementation, one for refactor (extract shared primitives, rename, tighten types).
- Maintain TDD discipline and craftsmanship standards (see `.cursor/rules/incubyte-tdd-discipline.mdc`, `.cursor/rules/incubyte-craftsmanship.mdc`).

## What this project is NOT

- Not multi-tenant. No schema switching, no `set_schema`.
- Not Django / DRF.
- Not deployed to AWS Lambda. (Pick any single-process deployment target; document the choice in `artifacts/tradeoffs.md`.)
- Not microservices. One backend, one frontend.
- Not enterprise auth. Out of scope unless requested.

## First commit must show TDD

When the build starts, the very first feature commit should look like:

```
test: empty employees endpoint returns []
feat: implement GET /employees returning empty list
```

…not:

```
feat: add CRUD for employees
```

The first kind passes the assessment. The second kind fails it.
