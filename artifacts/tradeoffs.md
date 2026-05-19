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
