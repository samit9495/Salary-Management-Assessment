# Backend Architecture

> FastAPI + SQLAlchemy 2.x + Pydantic v2 + SQLite. Single tenant. Single
> process. Boring on purpose.

For the testing approach see [testing-strategy.md](testing-strategy.md);
for analytics queries see [analytics-strategy.md](analytics-strategy.md);
for the rationale of every non-obvious choice see
[tradeoffs-and-decisions.md](tradeoffs-and-decisions.md).

## System sketch

```
+----------------+        HTTPS         +-------------------------+
|  React + Vite  | -------------------> |  FastAPI (uvicorn)      |
|  TanStack Q.   | <------------------- |  routes → services      |
|  shadcn / RTL  |                      |       ↓ repositories    |
+----------------+                      |       ↓   SQLAlchemy    |
                                        |       ↓     SQLite      |
                                        +-------------------------+
                                                 ↑
                                                 |  one-shot CLI
                                        +-------------------------+
                                        | scripts/seed.py         |
                                        | deterministic generator |
                                        | bulk insert + reset     |
                                        +-------------------------+
```

## Layering

```
app/api/routes/        thin: parse, dispatch, return Pydantic
        ↓
app/services/          use-case orchestration, transactions
        ↓
app/repositories/      SQLAlchemy queries (no business logic)
        ↓
app/models/            ORM (Numeric(12,2), unique email, indexes)
        ↓
app/db/                engine, SessionLocal, create_all on lifespan,
                       seed.py
```

The
[incubyte-fastapi-core rule](../../.cursor/rules/incubyte-fastapi-core.mdc)
enforces three hard constraints:

1. **Routes don't import SQLAlchemy.** Repository or service only.
2. **Services don't import FastAPI.** They take a `Session` (or
   repository) by constructor injection.
3. **One service call = one logical transaction.** Commits happen at
   the service boundary, never inside a repository.

## Module map

| Module | Responsibility |
|---|---|
| `app/main.py` | App factory, lifespan (`init_db`), CORS, middleware, exception handlers, router includes |
| `app/core/config.py` | Settings via `pydantic-settings`; `_parse_origins` handles both `a,b,c` and `["a","b"]` JSON-array forms |
| `app/core/exceptions.py` | `DomainError`, `EmployeeNotFound`, `DuplicateEmployeeEmail` |
| `app/core/logging.py` | `JsonFormatter`, idempotent `configure_logging`, contextvar-aware `request_id` |
| `app/db/base.py` | `DeclarativeBase` |
| `app/db/session.py` | `engine`, `SessionLocal`, `get_db()` dependency, `init_db()` |
| `app/db/seed.py` | Deterministic generator, bulk insert, `--reset` |
| `app/models/employee.py` | `Employee` ORM model |
| `app/schemas/employee.py` | `EmployeeBase`/`Create`/`Update`/`Read` with country/title validators |
| `app/schemas/analytics.py` | Compa-ratio + payroll + outlier response shapes |
| `app/repositories/employee_repository.py` | `add`, `get`, `update`, `delete`, `list`, `count`, `distinct_countries`, `apply_filters` (shared) |
| `app/services/employee_service.py` | CRUD orchestration; commits at boundary; raises domain exceptions |
| `app/services/salary_insights_service.py` | min/max/avg, top titles, payroll burden, NTILE outliers; `title_canonical` shared SQL expression |
| `app/services/compensation_analysis_service.py` | Window-function compa-ratio + range penetration |
| `app/api/routes/employees.py` | CRUD + `/employees/countries` + `/employees/compensation-analysis` |
| `app/api/routes/insights.py` | `/insights/country/...`, `/insights/payroll/...`, `/insights/outliers`, `/insights/global` |
| `app/api/middleware/request_context.py` | `X-Request-ID` propagation + access log (logs even on 500) |

## Data model

```
Employee
├── id          int, PK (no AUTOINCREMENT — rowid is enough)
├── full_name   str(120),  not null
├── job_title   str(120),  index
├── country     str(2),    index, uppercased on write
├── salary      Numeric(12,2), index
├── email       str(255)?, unique-index when present
├── department  str(120)?
├── hire_date   date?
├── is_active   bool, default True
├── created_at  datetime, server_default=func.now()
└── updated_at  datetime, server_default=func.now(), onupdate=func.now()
```

Indexes are added on the queries that demand them, not preemptively —
see [tradeoffs-and-decisions.md](tradeoffs-and-decisions.md) §"Indexes
column-by-column".

## Error handling

| Layer | Raises | Catches |
|---|---|---|
| Repository | `sqlalchemy.exc.*`, `NoResultFound` | nothing (bubbles up) |
| Service | `EmployeeNotFound`, `DuplicateEmployeeEmail` | DB errors only when there's a domain meaning |
| Route | nothing | nothing |
| `app/main.py` | global handlers | maps every `DomainError` subclass + a `Exception` fallback |

Error responses share one shape — `{ "detail": str, "code": str }` —
which the frontend's `apiFetch` reads to drive toast messages. See the
[incubyte-error-handling rule](../../.cursor/rules/incubyte-error-handling.mdc).

## Transactions

- Reads: no explicit transaction (default autocommit-ish via SQLite).
- Writes: services call `db.commit()` once at the end of the use case.
- `init_db()` runs `Base.metadata.create_all(engine)` in lifespan; no
  Alembic. The trade-off is documented; see
  [tradeoffs-and-decisions.md](tradeoffs-and-decisions.md) §"No
  migrations".

## Logging

- stdlib `logging` + `JsonFormatter` (~30 lines, no new deps).
- `RequestContextMiddleware` mints a per-request UUID, stashes it in
  `request_id_var: ContextVar`, attaches it to the response as
  `X-Request-ID`, and logs an `http_request` record on completion
  (including 500 paths — the access log lives in `finally`).
- Service logs: `INFO` on create/update/delete with safe identifiers;
  `WARN` on duplicate-email with hash-prefixed email (PII-safe).
- `LOG_SQL=true` raises `sqlalchemy.engine` to `DEBUG` for local
  debugging; off by default in production.
- See [tradeoffs-and-decisions.md](tradeoffs-and-decisions.md)
  §"Structured logging with stdlib".

## Health, CORS, lifespan

- `GET /` returns 200 (sanity / health).
- CORS: `allow_origins=settings.allowed_origins` with `X-Total-Count`
  and `X-Request-ID` in `expose_headers` so the frontend can read them.
- Lifespan: `init_db()` once on startup, single-shot — safe to call
  repeatedly because `create_all` is idempotent.

## What this design deliberately does NOT include

- No Alembic. `create_all` is sufficient for single-tenant SQLite.
- No async DB driver. SQLite + WSGI-style sync is faster for our
  workload than the overhead of `aiosqlite`.
- No background workers / Celery / Redis. The seed CLI is the only
  batch job and it runs in process.
- No tenant or schema switching. Removed from the ported Cursor rules
  during workspace setup; see
  [ai-assisted-workflow.md](ai-assisted-workflow.md).
- No global ORM base mixins (`TimestampMixin`, `SoftDelete`, etc.) —
  YAGNI for one table.

## See also

- [implementation-phases.md](implementation-phases.md) — phase-by-phase
  micro-task tables.
- [analytics-strategy.md](analytics-strategy.md) — the window function
  queries and NTILE outlier logic.
- [seed-performance-strategy.md](seed-performance-strategy.md) — the
  10k-row benchmark and its phase-level breakdown.
- [testing-strategy.md](testing-strategy.md) — pytest layout, fixtures,
  coverage gate.
