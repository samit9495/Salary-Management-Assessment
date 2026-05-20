# Trade-offs

One trade-off per heading. Add to this file as decisions are made. Each
entry: alternatives considered, choice, why, cost.

## SQLite as the primary database

**Considered**: SQLite, Postgres in Docker, MySQL.
**Picked**: SQLite (single file `app.db`, `Base.metadata.create_all`
on startup).
**Why**: Single-tenant tool with 10k rows. Postgres adds operational
overhead (container, port, healthcheck, migrations) for zero
functional benefit at this scale. SQLite ships with Python and is
trivially reset by deleting the file.
**Cost**: No concurrent writers, weak type enforcement (which Pydantic
covers at the boundary), no native `NUMERIC` precision (`Numeric(12,2)`
is stored as text-ish — fine for this volume).
**Reversibility**: Easy. SQLAlchemy abstracts the dialect; switch
`DATABASE_URL` and add migrations.

## Bulk-insert with SQLAlchemy Core for the seed script

**Considered**: ORM `Session.add_all`, executemany via raw `sqlite3`,
SQLAlchemy Core `insert(...).values([...])` in batches.
**Picked**: Core `insert()` in 1000-row batches with a single explicit
commit per chunk.
**Why**: ORM `add_all` was measured at roughly 10× slower because of
per-row attribute instrumentation; raw `sqlite3` would mean
maintaining a second schema definition. Core inserts give us the
speed and the schema source of truth in one place.
**Cost**: No `Employee` instances are returned — but the seed script
does not need them.
**Reversibility**: Easy. The bulk path is a private helper.

## Decimal (not float) for salary

**Considered**: `float`, `Decimal`, `int` cents.
**Picked**: `Decimal` with `Numeric(12, 2)` column and explicit
`quantize(Decimal("0.01"))` at the service boundary.
**Why**: Float arithmetic on money is a known foot-gun. `Decimal`
matches the assessment's craftsmanship rubric and Pydantic v2 serializes
it as a string so the wire format stays exact.
**Cost**: Slight performance cost vs `int` cents, and we lose the
"all-currency-in-one-unit" simplicity.
**Reversibility**: Easy at the column level; service contracts already
return `Decimal`.

## `X-Total-Count` header instead of an envelope response

**Considered**: `{ data: [...], total: N, limit, offset }` envelope vs
flat list + `X-Total-Count` header.
**Picked**: Flat list + header (and CORS-expose it so the SPA can read it).
**Why**: Matches the GitHub/RFC convention and keeps `list[EmployeeRead]`
as the response schema, which makes the OpenAPI doc and the typed
frontend client trivial.
**Cost**: Slightly less self-describing for one-off API consumers who
don't read response headers.
**Reversibility**: Easy — swap the route handler and a one-off
TanStack Query wrapper.

## TanStack Query for server state, React state for UI state

**Considered**: Redux Toolkit + RTK Query, Zustand, raw `useEffect` +
`fetch`.
**Picked**: TanStack Query for everything that comes from the API;
local `useState` for filter/pagination/dialog UI state.
**Why**: TanStack Query gives us caching, invalidation, retry, loading
flags, and an explicit error path with about ten lines of setup per
endpoint. A global store is overkill for a single-tenant CRUD tool.
**Cost**: Two paradigms coexist (queries + setState). Fine because the
boundary is obvious — anything async lives in `hooks/use*`.
**Reversibility**: Easy. Hooks could be ported to a global store later.

## Vitest + React Testing Library, no snapshot tests

**Considered**: Jest, Cypress component testing, Storybook + Chromatic.
**Picked**: Vitest + RTL + `userEvent`, with behavioral assertions only
(`getByRole`, `findByText`).
**Why**: Vitest piggybacks on Vite — no separate transformer chain. RTL
forces tests to describe what the user can do, not what the DOM
happens to look like. The Incubyte testing rule explicitly forbids
snapshot tests because they pin layout, not behavior.
**Cost**: Visual regressions are invisible to the suite — relying on
the manual smoke scenarios for those.
**Reversibility**: Easy.

## Structured logging with stdlib, not structlog or an SDK

**Considered**: stdlib `logging` + custom `JsonFormatter`, `structlog`,
`loguru`, third-party APMs (Sentry, Datadog, OpenTelemetry).
**Picked**: stdlib `logging` with a small `JsonFormatter` and a
`request_id_var: ContextVar`, mounted via `RequestContextMiddleware`.
**Why**: zero new dependencies, fits the "boring solution wins" rule.
The formatter is ~30 lines, idempotent `configure_logging` only touches
handlers it owns (so pytest's `caplog` keeps working), and Fly captures
stdout, so log shipping is the platform's job. Sentry/Datadog buys
real value but is out of scope for a single-tenant assessment tool.
**Cost**: No structured ingest UI; queries are `fly logs | jq`. No
distributed tracing. No automatic per-call sampling.
**Reversibility**: Easy. The formatter is one file; swap to structlog
or pipe to OTLP without touching call sites — every record already
carries `request_id` and structured fields.

## Case-insensitive job-title normalization in queries, not in storage

**Considered**: (a) lower-case `job_title` on write and store the
canonical form; (b) keep original casing and group by `LOWER(job_title)`
at query time; (c) add a generated/derived column and a functional
index.
**Picked**: (b) — store original, group via a shared
`title_canonical = func.lower(Employee.job_title)` expression, then
`display_title()` title-cases the canonical key on the response.
**Why**: Lossless storage (HR may legitimately enter "iOS Engineer" vs
"Ios Engineer") plus a single source of truth for grouping. The
expression is defined once at the service module level and reused by
`average_salary_by_country_and_title`, `top_titles_by_count`,
`payroll_by_title`, and `salary_outliers`.
**Cost**: `LOWER()` defeats the existing `ix_employees_job_title` btree.
At 10k rows the difference is < 1ms; for >100k rows the right answer is
a functional index on `lower(job_title)` (SQLite supports them; Postgres
does too).
**Reversibility**: Easy. If we later normalize on write, the query-time
`LOWER()` becomes a no-op, not a regression.

## Case-insensitive country: schema validator + route uppercase

**Considered**: (a) `BeforeValidator` only on Pydantic schemas; (b)
uppercase in the route layer only; (c) uppercase at every entry point.
**Picked**: (c) — `BeforeValidator` on `EmployeeBase.country` and
`EmployeeUpdate.country` covers POST/PUT bodies, and `country.upper()`
on the route uses the query/path param. The Insights page input also
already lives behind `CountryCombobox` which only emits canonical codes.
**Why**: SQLite collates case-sensitively by default; consistent storage
casing keeps the existing index useful and the per-country group counts
deterministic. Doing the cast at both the schema and the route stops
weak callers (e.g. curl) from polluting the DB.
**Cost**: A trivial duplication (one validator, one `.upper()` in the
route handler). Acceptable for a hard invariant.
**Reversibility**: Easy.

## Compa-Ratio / Range Penetration as a separate endpoint

**Considered**: (a) embed peer aggregates in every `GET /employees` row;
(b) add a dedicated `GET /employees/compensation-analysis` endpoint;
(c) expose only per-employee `GET /employees/{id}/compensation-analysis`.
**Picked**: (b) — a per-batch endpoint that accepts the same `country`
and `q` filters as `/employees` and returns a per-id map.
**Why**: Keeps the list endpoint slim and cacheable (rows rarely change
on every keystroke; peer aggregates do). The window-function query is
O(n) over the filtered subset, so the analyses array always has the
same scope as what the table will render. The frontend joins on `id` —
no client-side aggregation.
**Cost**: Two HTTP requests per page render. Acceptable: TanStack Query
runs them in parallel and shares the cache across navigations. We could
gate it behind a `?include=analysis` flag if HR ever needs to skip the
analytics.
**Reversibility**: Easy. Embedding later would be a flag plus a
`response_model` extension; the service stays unchanged.

## NTILE(20) for outlier detection, with `min_group_size` guard

**Considered**: (a) absolute thresholds (e.g. salary < median * 0.5);
(b) percentile bucketing (NTILE); (c) z-scores per group.
**Picked**: (b) — `NTILE(20) OVER (PARTITION BY country, lower(title)
ORDER BY salary)`, return bucket 1 as bottom 5% and bucket 20 as top.
Skip groups smaller than `min_group_size` (default 5).
**Why**: NTILE is shape-agnostic so it works on uneven distributions
(no normality assumption). Bucketing per peer group keeps the comparison
fair — a junior in IN isn't flagged because they earn less than a
principal in US. The group-size guard removes the "lone employee is
both top and bottom" noise.
**Cost**: Tiny peer groups (e.g. one Designer in a country) are silent
— intentional. NTILE in SQLite is O(n log n) per partition; at 10k rows
it's microseconds.
**Reversibility**: Easy. Service method is a single query; threshold
strategy could be swapped behind the same `salary_outliers(...)`
signature.

## shadcn-style `Combobox` built on cmdk + Radix Popover

**Considered**: (a) hand-rolled `<select>` with `<datalist>` styling;
(b) a third-party react-select; (c) shadcn primitives (`cmdk` +
`@radix-ui/react-popover`).
**Picked**: (c) — generic `Combobox` + concrete `CountryCombobox`
backed by a new `GET /employees/countries` endpoint that reuses the
exact same `_filtered` chain as `GET /employees`.
**Why**: Native `<datalist>` has poor keyboard semantics on mobile
Safari and can't show the per-option count. react-select drags in a
heavy CSS-in-JS runtime; cmdk + Radix Popover are accessible by default
(combobox role, ARIA expanded, keyboard navigation) and only ship the
primitives we actually mount.
**Cost**: Two new deps (~25 KB gzipped together); jsdom test setup
needed `ResizeObserver` / `PointerEvent` / `scrollIntoView` polyfills.
**Reversibility**: Generic `Combobox` is one file; could be replaced
without touching `CountryCombobox` consumers.

## Stitch MCP as a UI starting point, hand-refined every component

**Considered**: Hand-write every component, generate with Stitch and
commit as-is, generate with Stitch and refine.
**Picked**: Generate with Stitch as a draft, then split into small TDD
commits (failing component test → minimal component → refactor).
**Why**: The assessment is graded on TDD discipline and craftsmanship.
A blindly-committed Stitch dump would fail the commit-log audit and
duplicate styling everywhere.
**Cost**: Slower than a one-shot dump; faster than from-scratch.
**Reversibility**: N/A — generated code lives in the diff like any other.
