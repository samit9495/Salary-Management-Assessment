# Tasks — Todo

Per `.cursor/rules/ai-workflow.mdc`, every session that touches code adds a dated entry here and moves it to `## Completed` when done.

## In Progress

_(none — add the next ticket/task here)_

## Backlog

_(seed with whatever the user hands you next; the implementation work is not started yet)_

## Completed

### 2026-05-20 — Bug fixes & advanced HR analytics
- [x] Phase A — title-case insensitivity in aggregations (shared `title_canonical` + `display_title`)
- [x] Phase B — country-case insensitivity (Pydantic `BeforeValidator`, route uppercasing)
- [x] Phase C — reusable `SalaryBarChart` with `YAxis width=80` + compact tick formatter; `TitleAveragesChart` delegates
- [x] Phase D — `apiFetchWithMeta`, `employeesApi.list → {rows,total}`, `<Pagination>` accepts `total` and renders "Showing X–Y of N"
- [x] Phase E — shadcn `Popover` + `Command` primitives, `GET /employees/countries`, generic `Combobox` + `CountryCombobox` wired into Employees and Insights pages
- [x] Phase F — `CompensationAnalysisService` (window function), `GET /employees/compensation-analysis`, `CompaRatioBadge` + `RangePenetrationBar` columns
- [x] Phase G — payroll burden service + `/insights/payroll/by-country|by-title` + `PayrollBreakdown` section
- [x] Phase H — NTILE(20) `salary_outliers`, `/insights/outliers`, bottom/top `OutlierTables`
- [x] Phase I — `artifacts/tradeoffs.md` (5 new entries), `tasks/manual-test-scenarios.md` (7 new), `README` API table, `tasks/lessons.md`
- **Status**: done
- **Summary**: 47 commits across 9 phases, all `test:` → `feat:`/`refactor:` cadence. Backend grew from 100 to 127 passing tests; frontend from 50 to 71. Two new deps (`cmdk`, `@radix-ui/react-popover`) and one new vitest polyfill block.

### 2026-05-20 — Structured JSON logging across backend and frontend
- [x] `app/core/logging.py` — `JsonFormatter`, `request_id_var`, idempotent `configure_logging(level, sql_echo)`
- [x] `Settings.log_level` / `Settings.log_sql` (env-driven) and lifespan wiring
- [x] `RequestContextMiddleware` with `X-Request-ID` correlation and one structured access line per request
- [x] Global `Exception` handler (ERROR + traceback) and WARN log on the existing `DomainError` handler
- [x] `EmployeeService` create/update/delete INFO logs with safe identifiers; duplicate-email WARN with SHA-256 prefix
- [x] `LOG_SQL=true` raises `sqlalchemy.engine` to DEBUG via the same formatter
- [x] Seed CLI emits `seed_start` / `seed_finish` JSON events
- [x] Frontend `src/lib/logger.ts` (info no-op in prod), `apiFetch` `api_error` log with request-id correlation, top-level `ErrorBoundary`
- [x] `Dockerfile` and `fly.toml` expose `LOG_LEVEL` / `LOG_SQL`; uvicorn CMD switched to `--no-access-log`
- [x] README "Logging" section documenting format, instrumented checkpoints, and env knobs
- **Status**: done
- **Summary**: 13 RED→GREEN pairs (plus one `chore:` to un-shadow `frontend/src/lib/` from `.gitignore`). Backend grew from 70 to 100 tests, frontend from 24 to 37; everything green.

### 2026-05-20 — Salary Management end-to-end build
- [x] Phase 0  — environment bootstrap (Python 3.12 venv, backend + frontend stack verified)
- [x] Phase 1  — backend foundation (FastAPI, Settings, DB session, domain exceptions, CORS, lifespan)
- [x] Phase 2  — Employee CRUD (model, repo, service, all 5 endpoints, pagination/filter/sort/search, 404/409)
- [x] Phase 3  — Salary insights (avg/min/max/count by country, avg by (country,title), top titles)
- [x] Phase 4  — Seed script (deterministic, bulk insert, `--reset`, CLI, perf budget test)
- [x] Phase 5  — Frontend foundation (Vite + TS strict, Tailwind v4, TanStack Query, Router, Vitest)
- [x] Phase 6  — Employees UI (table, filters, RHF + Zod form, create/edit/delete, error toasts)
- [x] Phase 7  — Insights UI (country selector, KPI cards, by-title bar chart)
- [x] Phase 8  — Dashboard (overview KPIs + recent hires + country distribution chart)
- [x] Phase 9  — Cross-cutting hardening (X-Total-Count header, CORS expose, indexes already in model)
- [x] Phase 10 — QA + coverage (Pagination + Filters tests, manual scenarios doc; backend 99% line coverage)
- [x] Phase 11 — Documentation (README, architecture, trade-offs, prompts log)
- [x] Phase 12 — Deployment (Dockerfile, fly.toml, vercel.json, env example, comma-separated origins)
- [x] Phase 13 — Final commit-log audit + tasks sweep
- **Status**: done
- **Summary**: 95 commits, clean test/feat/refactor cadence. Backend 69 tests
  + 99% line coverage; frontend 24 tests; seed 10k rows in 0.09s
  (budget 5s). Deployment artifacts ready for Fly.io + Vercel.

### 2026-05-20 — Artifact audit step + post-commit reminder hook
- [x] Add Step 9 (Artifact audit) to `.cursor/skills/incubyte-tdd-loop/SKILL.md` (renumbered Loop-back to Step 10)
- [x] Add `scripts/git-hooks/post-commit` reminder script (executable, no-op when nothing matches)
- [x] Add `scripts/git-hooks/README.md` with one-time install instructions (`git config core.hooksPath scripts/git-hooks`)
- **Status**: done
- **Summary**: TDD loop now ends with a 60s artifact-audit checkpoint; opt-in post-commit hook nags on `perf:` / `docs(stitch):` / `!:` / `tradeoff:|decision:|considered:` body. Smoke-tested against 8 trigger subjects + 5 silent ones.

### 2026-05-20 — Cursor workspace bootstrap
- [x] Created `.cursor/{rules,skills,agents,plans}` with Incubyte TDD-first + craftsmanship setup
- [x] Created `tasks/`, `artifacts/`, `AGENTS.md` companion files
- **Status**: done
- **Summary**: Cursor rules/skills/agents in place; ready to start the Salary Management build with TDD.

## Entry template

```
### YYYY-MM-DD — <ticket or title>
- [ ] Sub-task
- [ ] Sub-task
- **Status**: in-progress | done
- **Summary**: <one-line outcome when done>
```
