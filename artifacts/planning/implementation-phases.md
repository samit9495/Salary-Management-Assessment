# Implementation Phases

> The phase-by-phase TDD breakdown — distilled from the 540-line
> [execution plan](../../.cursor/plans/salary_mgmt_execution_plan_4021925a.plan.md)
> and the six follow-on plans that drove the bugs/analytics, UX
> polish, logging, seed perf validation, review-warnings, and
> documentation consolidation passes.

For the chronological narrative see [roadmap.md](roadmap.md); for the
discipline these phases run under see [testing-strategy.md](testing-strategy.md).

## Operating model (per micro-task)

```
1. RED      — smallest failing test, one assertion
2. COMMIT     test: <behavior>
3. GREEN    — minimum code to pass; run the full suite
4. COMMIT     feat:|fix: <behavior>
5. REFACTOR — improve structure; re-run all tests
6. COMMIT     refactor: <what improved>   (only if anything changed)
```

One TDD step = one commit. The
[incubyte-tdd-loop skill](../../.cursor/skills/incubyte-tdd-loop/SKILL.md)
is the one-screen recipe.

## Phase 0 — Workspace + environment bootstrap

Setup that happens before any feature code is written.

| # | Objective | Files | Verify |
|---|---|---|---|
| 0.1 | Port Cursor rules / skills / agents from a prior project; add new TDD/craftsmanship/commit-hygiene rules | `.cursor/rules/`, `.cursor/skills/`, `.cursor/agents/` | All `.mdc` parse; `incubyte-tdd-discipline.mdc` is always-apply |
| 0.2 | Create `.venv`, pin Python 3.11+ + Node 20 | `.venv/`, `.python-version`, `frontend/.nvmrc` | `python -c "import fastapi, sqlalchemy"` passes |
| 0.3 | Verify backend stack | `pyproject.toml` | `python -c "from app.main import app"` |
| 0.4 | Verify frontend stack | `frontend/package.json` | `cd frontend && npm ls --depth=0` no MISSING |

See [ai-assisted-workflow.md](ai-assisted-workflow.md) for the rule /
skill / agent inventory.

## Phase 1 — Backend foundation (8 micro-tasks)

| # | Objective | Files | Test(s) |
|---|---|---|---|
| 1.1 | `pyproject.toml` with verified stack | `pyproject.toml` | chore |
| 1.2 | Empty FastAPI app boots | `app/main.py`, `tests/integration/test_health.py` | `test_root_returns_200` |
| 1.3 | Settings via `pydantic-settings` | `app/core/config.py` | `test_settings_loads_database_url` |
| 1.4 | `Base` + engine + `get_db()` | `app/db/base.py`, `app/db/session.py` | `test_get_db_yields_and_closes` |
| 1.5 | In-memory SQLite test fixtures | `tests/conftest.py` | `test_db_fixture_is_clean_per_test` |
| 1.6 | Domain exception + global handler | `app/core/exceptions.py` | `test_domainerror_maps_to_500_with_code` |
| 1.7 | Lifespan creates tables | `app/main.py` | `test_tables_exist_after_startup` |
| 1.8 | CORS for `http://localhost:5173` | `app/main.py`, `app/core/config.py` | `test_cors_preflight_for_frontend_origin` |

## Phase 2 — Employee CRUD (~18 micro-tasks)

Builds up the `Employee` model one column per test, with full
`POST/GET/PUT/DELETE /employees` ending in pagination + filter +
search + sort.

| # | Objective | Test(s) |
|---|---|---|
| 2.1 | `Employee` minimal model | `test_employee_table_created` |
| 2.2 | `EmployeeCreate` / `EmployeeRead` schemas | `test_schema_rejects_negative_salary`, `test_schema_requires_iso2_country` |
| 2.3 | `EmployeeRepository.add` + `get` | `test_add_persists`, `test_get_none_when_missing` |
| 2.4 | `EmployeeService.create` (commits at boundary) | `test_service_create_returns_persisted_employee` |
| 2.5 | `POST /employees` 201 | `test_create_returns_201_with_persisted_row` |
| 2.6 | 422 on invalid payload | `test_invalid_salary_returns_422` |
| 2.7 | `GET /employees/{id}` happy path | `test_get_employee_by_id_returns_200` |
| 2.8 | `EmployeeNotFound` → 404 | `test_get_returns_404_when_missing` |
| 2.9–2.11 | `GET /employees` empty → rows → paginated | three RED-GREEN pairs |
| 2.12 | Filter `?country=` | `test_list_filters_by_country` |
| 2.13–2.14 | `PUT /employees/{id}`, `DELETE /employees/{id}` | update + delete + 404 paths |
| 2.15 | Unique email + `DuplicateEmployeeEmail` → 409 | `test_create_with_duplicate_email_returns_409` |
| 2.16 | Optional `department`, `hire_date`, `is_active` | `test_defaults_is_active_true` |
| 2.17 | Filter `?q=` (case-insensitive name search) | `test_list_filters_by_name_substring` |
| 2.18 | Sort `?sort=salary,-hire_date` allow-list | `test_unknown_sort_returns_422` |

**Refactor checkpoints**: extract `_to_read()` helper, extract
`EmployeeService._get_or_raise()`, confirm repository has no business
logic.

## Phase 3 — Salary insights (~12 micro-tasks)

| # | Objective | Test(s) |
|---|---|---|
| 3.1 | `average_by_country` returns `Decimal("0.00")` when empty | `test_average_zero_when_no_employees` |
| 3.2 | Mean excludes other countries | `test_average_excludes_other_countries` |
| 3.3 | `min/max_by_country` | `test_min_max_by_country` |
| 3.4 | `average_by_country_and_title` | `test_avg_by_country_and_title` |
| 3.5 | `GET /insights/country/{code}` returns `{min,max,avg,count}` | `test_insights_country_returns_payload_shape` |
| 3.6 | 422 on malformed country | `test_insights_country_rejects_3_letter_code` |
| 3.7 | `GET /insights/country/{code}/title/{title}` | `test_insights_country_title_returns_avg` |
| 3.8 | Top titles by avg salary | `test_top_titles_returns_sorted_by_avg_desc` (LLM Council checkpoint) |
| 3.9 | N+1 absent (single-query) | `test_insights_endpoint_uses_single_query` |

## Phase 4 — Seed script (~9 micro-tasks)

| # | Objective | Test(s) |
|---|---|---|
| 4.1 | Drop `data/first_names.txt` + `last_names.txt` | `test_seed_data_files_exist` |
| 4.2 | `seed(db, count=N)` inserts N | `test_seed_inserts_expected_row_count` |
| 4.3 | Deterministic with `seed=42` | `test_seed_is_deterministic_with_seed` |
| 4.4 | Names from provided files only | `test_seed_uses_only_provided_first_names` |
| 4.5 | `--reset` truncates | `test_seed_reset_clears_table` |
| 4.6 | CLI entry point | `test_seed_cli_invokes_with_args` |
| 4.7 | Opt-in perf budget | `test_seed_performance_budget_under_5s` (`-m perf`) |
| 4.8 | Benchmark + record | append to [seed-performance-strategy.md](seed-performance-strategy.md) |
| 4.9 | `RuntimeError` when name files empty | `test_run_raises_runtime_error_when_name_files_are_empty` (added in QA pass) |

## Phase 5 — Frontend foundation (~7 micro-tasks)

| # | Objective | Test(s) |
|---|---|---|
| 5.1 | Vite + React + TS strict scaffold | chore |
| 5.2 | Install verified deps (RTQ, Table, Recharts, Router, RHF, Zod, Vitest, RTL) | chore |
| 5.3 | Tailwind + shadcn init | chore |
| 5.4 | Vitest + RTL setup smoke | `test_setup_loads_jest_dom` |
| 5.5 | `QueryClientProvider` + `BrowserRouter` | `test_app_renders_router_outlet` |
| 5.6 | Typed `apiFetch` + `ApiError` | `test_api_throws_ApiError_on_4xx` |
| 5.7 | `employees` + `insights` services | `test_employees_list_builds_querystring` |

## Phase 6 — Employees UI (~10 micro-tasks)

`AppShell` + `EmployeesPage` with table, country filter, pagination,
RHF+Zod form, create/edit/delete dialogs, toast on API error. The
`AppShell` and form are Stitch-assisted drafts split into TDD-paired
commits per
[tradeoffs-and-decisions.md](tradeoffs-and-decisions.md) §"Stitch MCP
as a UI starting point".

## Phase 7 — Insights UI (~7 micro-tasks)

`CountrySelect`, `useInsightsByCountry` hook, `KpiCards`,
`TitleAveragesChart` (Recharts), `InsightsPage` composition,
empty/loading/error states.

## Phase 8 — Dashboard (~4 micro-tasks)

`GET /insights/global` endpoint + `GlobalKpi` widget,
`RecentEmployees` (limit 10), `CountryDistribution` chart,
`DashboardPage` composition.

## Phase 9 — Bugs + advanced HR analytics (~52 commits)

Driven by the
[salary-mgmt bugs and analytics plan](../../.cursor/plans/salary-mgmt_bugs_and_analytics_2c8dd4b6.plan.md).

| Sub-phase | Outcome | Highlights |
|---|---|---|
| A — Title case | Aggregate by `lower(title)`, display title-cased | Shared `title_canonical` expression |
| B — Country case | `BeforeValidator` + route uppercase | All entry points covered |
| C — Recharts Y-axis | Reusable `<SalaryBarChart>` with safe `YAxis width=80` | Eliminates label clipping |
| D — Pagination "of N" | `apiFetchWithMeta` reads `X-Total-Count` | `<Pagination>` accepts `total` |
| E — Country combobox | `cmdk` + Radix `Popover`; `useDistinctCountries` hook | `GET /employees/countries` endpoint |
| F — Compa-Ratio + Range Penetration | Window-function service + separate endpoint | `CompaRatioBadge` + `RangePenetrationBar` |
| G — Payroll burden | `payroll_by_country/title` + `<PayrollBreakdown>` | Percentages sum to 100 |
| H — Outliers | `NTILE(20)` with `min_group_size=5` | `<OutlierTables>` Bottom/Top |
| I — Docs sweep | `artifacts/tradeoffs.md` + manual scenarios | Lessons logged |

See [analytics-strategy.md](analytics-strategy.md) for the metric
math and [ui-ux-decisions.md](ui-ux-decisions.md) for the chart wrapper.

## Phase 10 — UX polish + Title Case sweep (~12 commits)

Driven by the
[insights polish ux-pass plan](../../.cursor/plans/insights-polish-ux-pass_c3887b4e.plan.md).

| Sub-phase | Outcome |
|---|---|
| J — Primitives | `<AnalyticsSection>` + `<InfoHint>` + shadcn `tooltip.tsx` |
| K — Title Case sweep | Single `refactor:` commit standardizing user-visible headings |
| L — Insights restructure | Vertical-stacked payroll; tooltips; card wrappers |
| M — Dashboard tooltips | `Employees by Country` + `Recent Hires` in `<AnalyticsSection>` |
| N — Employees table | `columns` type widened to `string \| ReactNode`; `<InfoHint>` on Compa / Spread |
| O — Payroll readability | `<SummaryList>` extracted; `<PayrollBreakdown>` + Dashboard `RecentHires` reuse it |

See [ui-ux-decisions.md](ui-ux-decisions.md) for the design rationale.

## Phase 11 — Logging + observability (~14 micro-tasks)

Driven by the
[logging implementation plan](../../.cursor/plans/backend_frontend_logging_implementation_7a69693d.plan.md).

| Sub-phase | Outcome |
|---|---|
| Core | `JsonFormatter` + idempotent `configure_logging` |
| Settings | `LOG_LEVEL`, `LOG_SQL` |
| Lifespan | Invokes `configure_logging` once |
| Middleware | `RequestContextMiddleware` + `X-Request-ID` + access log |
| Handlers | Global `Exception` handler + WARN on `DomainError` |
| Services | INFO on mutations; WARN on duplicate email (hash-prefixed) |
| SQL echo | `LOG_SQL=true` raises `sqlalchemy.engine` to DEBUG |
| Seed | `seed_start` / `seed_finish` structured logs |
| Frontend | `src/lib/logger.ts` + `<ErrorBoundary>` + `api_error` on non-OK |
| Deploy | `LOG_LEVEL` / `LOG_SQL` in fly.toml + `--no-access-log` |
| Docs | README "Logging" section |

## Phase 12 — Review warnings + QA pass (~7 commits)

Driven by the
[address-review-warnings plan](../../.cursor/plans/address-review-warnings_864a30e2.plan.md)
and a [QA Automation agent](../../.cursor/agents/incubyte-qa-automation.md)
run.

| Sub-phase | Outcome |
|---|---|
| W1 + I2 | Rename `_filtered` → `apply_filters`; cross-ref `title_canonical` |
| W2 | Characterization test exposed real bug; moved access log to `finally` |
| W3 | `TypedDict` return shapes for `payroll_by_*`, `global_overview`, `salary_outliers`; drop route-side `# type: ignore` |
| W4 | SQLAlchemy 2.x `delete()` in seed tests |
| I1 | Remove unused `_ALLOWED_SORT_VALUES` |
| QA bug 1 | `ALLOWED_ORIGINS` JSON-array parsing — `json.loads()` branch added |
| QA bug 2 | `name-files-empty` characterization test added |
| QA hygiene | Extract `*.utils.ts` for Fast Refresh; `.gitignore` coverage; drop dead `eslint-disable` |

## Phase 13 — Seed perf validation (~3 commits)

Driven by the
[seed-10k-perf-validate plan](../../.cursor/plans/seed-10k-perf-validate_dcbc7a0c.plan.md).

Re-ran the 10k seed three times; produced a phase-level breakdown via
a throwaway `scripts/_bench_seed.py`; appended a dated entry to
[seed-performance-strategy.md](seed-performance-strategy.md). Verdict:
no architectural change needed; one nice-to-have noted for the 100k+
regime.

## Phase 14 — Documentation consolidation (this directory)

The output of this phase is the curated planning surface you're
reading. See [README.md](README.md) for the index.

## Where the audit trail lives

- **Raw plans** → [../../.cursor/plans/](../../.cursor/plans/)
- **Driving prompts** → [../prompts/driving-prompts.md](../prompts/driving-prompts.md)
- **Working session notes** → [../../tasks/lessons.md](../../tasks/lessons.md)
- **Manual scenarios** → [../../tasks/manual-test-scenarios.md](../../tasks/manual-test-scenarios.md)
- **Performance log** → [seed-performance-strategy.md](seed-performance-strategy.md)
