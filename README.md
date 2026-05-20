# Salary Management

A small but production-quality salary management tool for an HR manager of
an organization with 10,000 employees. Built for the Incubyte assessment;
graded on visible TDD evolution in `git log`, software craftsmanship,
and an end-to-end working stack.

> **Spec**: `Salary Management Assessment.pdf` at the repo root.
> **Agent brief**: [`AGENTS.md`](./AGENTS.md).

## Stack

| Layer    | Choice                                                   |
| -------- | -------------------------------------------------------- |
| Backend  | Python 3.11+, FastAPI, SQLAlchemy 2.x, Pydantic v2        |
| Database | SQLite (single file, single tenant)                       |
| Frontend | React 19 + Vite + TypeScript (strict), Tailwind, shadcn/ui, TanStack Query, Recharts |
| Tests    | pytest + httpx `TestClient` (backend), Vitest + RTL (frontend) |
| Seed     | 10k employees, bulk insert, deterministic via `--seed`    |

## Repository layout

```
.
├── app/                      FastAPI backend (routes → services → repositories → models)
├── tests/                    Backend tests (unit + integration + seed)
├── scripts/                  CLI helpers (seed.py)
├── frontend/                 React + Vite SPA
├── data/                     first_names.txt / last_names.txt seed inputs
├── artifacts/                planning notes, prompts, performance log, trade-offs
├── tasks/                    todo, lessons learned, manual test scenarios
└── .cursor/                  rules, skills, agents that drive the AI workflow
```

## Quickstart

### 1. Backend

```bash
# create + activate a Python 3.11+ venv
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"

# create tables + seed 10k employees deterministically
python -m scripts.seed --count 10000 --seed 42 --reset

# run the API (auto-creates tables on startup via lifespan)
uvicorn app.main:app --reload --port 8000
```

The API listens on <http://localhost:8000>. Interactive docs:
<http://localhost:8000/docs>.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev   # http://localhost:5173
```

The frontend talks to <http://localhost:8000> by default. To override,
set `VITE_API_URL` in `frontend/.env.local`.

### 3. Tests

```bash
# Backend (run from repo root with the venv activated)
pytest                                    # 69 tests, ~1s
pytest --cov=app --cov-report=term-missing  # 99% line coverage

# Frontend
cd frontend
npm run test
npm run test:coverage
```

## API surface

| Method | Path                                                          | Purpose                                                         |
| ------ | ------------------------------------------------------------- | --------------------------------------------------------------- |
| `GET`  | `/`                                                           | Health                                                          |
| `POST` | `/employees`                                                  | Create                                                          |
| `GET`  | `/employees?country=&q=&sort=&limit=&offset=`                 | List (`X-Total-Count` header; country is case-insensitive)      |
| `GET`  | `/employees/countries?country=&q=`                            | Distinct countries with counts under the same filter chain      |
| `GET`  | `/employees/compensation-analysis?country=&q=`                | Per-id compa-ratio + range-penetration via window function      |
| `GET`  | `/employees/{id}`                                             | Get one (404 if missing)                                        |
| `PUT`  | `/employees/{id}`                                             | Partial update                                                  |
| `DELETE` | `/employees/{id}`                                           | Delete                                                          |
| `GET`  | `/insights/by-country/{country}`                              | avg / min / max / count (path is case-insensitive)              |
| `GET`  | `/insights/by-country/{country}/by-title`                     | avg salary per job title within a country (titles case-folded)  |
| `GET`  | `/insights/top-titles?limit=`                                 | most common job titles                                          |
| `GET`  | `/insights/overview`                                          | Org-wide KPIs                                                   |
| `GET`  | `/insights/recent?limit=`                                     | most recently created employees                                 |
| `GET`  | `/insights/distribution`                                      | per-country employee counts                                     |
| `GET`  | `/insights/payroll/by-country`                                | total + per-country payroll burden with percentages             |
| `GET`  | `/insights/payroll/by-title`                                  | total + per-title payroll burden with percentages               |
| `GET`  | `/insights/outliers?bucket=bottom\|top&min_group_size=&limit=` | NTILE(20) per peer group: bottom 5% / top 5% compensated         |

Errors share a uniform shape: `{"detail": "...", "code": "..."}` —
`employee_not_found` (404), `duplicate_email` (409), Pydantic validation (422).

## Logging

The backend emits one structured JSON line per log record on stdout —
no file rotation, no third-party SDK, just stdlib `logging` formatted
through `app/core/logging.py:JsonFormatter`. Sample line:

```json
{"timestamp":"2026-05-20T03:44:11.482+00:00","level":"INFO","logger":"app.api.middleware.request_context","message":"http_request","request_id":"a3f1b9...","method":"GET","path":"/employees","status_code":200,"duration_ms":7.412}
```

What's instrumented:

| Source                                     | Level   | Event                                                              |
| ------------------------------------------ | ------- | ------------------------------------------------------------------ |
| `RequestContextMiddleware`                 | INFO    | one `http_request` line per request (DEBUG for `GET /` health)     |
| `EmployeeService.create/update/delete`     | INFO    | `employee_created` / `employee_updated` / `employee_deleted`       |
| Duplicate email path                       | WARNING | `duplicate_email` with an 8-char SHA-256 prefix (no raw email)     |
| `DomainError` exception handler            | WARNING | the failing `code`, status, request method/path                    |
| Global `Exception` handler                 | ERROR   | `unhandled_exception` plus full traceback via `logger.exception()` |
| `scripts/seed.py`                          | INFO    | `seed_start` and `seed_finish` (with `inserted` and `elapsed_s`)   |

Every record carries the request-scoped `request_id` (UUID generated on
the way in or echoed from an inbound `X-Request-ID` header). The same id
is returned to the client in the `X-Request-ID` response header so a
user-visible error can be grepped straight out of `fly logs`.

The frontend has a small `src/lib/logger.ts` wrapper around `console`
that drops `info` calls in production builds (`import.meta.env.PROD`)
while always keeping `warn` and `error`. `apiFetch` logs an `api_error`
for every non-OK response (`method`, `path`, `status`, `requestId`), and
a top-level `ErrorBoundary` logs `react_error_boundary` and renders a
fallback card so render-time failures don't blank the page.

### Configuration

| Variable    | Default | Effect                                                  |
| ----------- | ------- | ------------------------------------------------------- |
| `LOG_LEVEL` | `INFO`  | root logger level. `DEBUG` to see request-handler debug |
| `LOG_SQL`   | `false` | when `true`, raises `sqlalchemy.engine` to DEBUG so emitted SQL flows through the JSON formatter |

The Docker `CMD` passes `--no-access-log` to uvicorn so we don't
double-log the request line; rely on the middleware's structured entry
instead.

## How this was built

This codebase was built test-first. Every behavior change has a
`test:` commit immediately followed by the `feat:` / `fix:` commit that
makes it pass, sometimes followed by a `refactor:` commit. To audit:

```bash
git log --oneline
```

You'll see a clean Red-Green-Refactor evolution, one commit per logical
step. See [`tasks/lessons.md`](./tasks/lessons.md) for things learned
along the way and [`artifacts/tradeoffs.md`](./artifacts/tradeoffs.md)
for design decisions that had real alternatives.

## Performance budget

Seeding 10,000 rows must complete in **under 5 seconds** on a typical
dev laptop. Current measurement: **0.09 s** for 10k, **0.46 s** for 50k
on Apple Silicon. See [`artifacts/performance.md`](./artifacts/performance.md).

## Deployment

### Backend — Fly.io

```bash
fly launch --copy-config --no-deploy           # uses fly.toml in the repo
fly volumes create salary_data --size 1 --region bom
fly secrets set ALLOWED_ORIGINS="https://<your-vercel-domain>"
fly deploy

# seed the production volume (one-shot, deterministic)
fly ssh console -C "python -m scripts.seed --count 10000 --seed 42 --reset"
```

The `Dockerfile` is multi-arch-friendly and mounts the SQLite file on the
`/data` volume, so the data survives machine restarts. Health check hits
`/`.

### Frontend — Vercel

```bash
cd frontend
vercel link
vercel env add VITE_API_URL  # https://<your-fly-app>.fly.dev
vercel --prod
```

`vercel.json` rewrites all paths to `index.html` so client-side routing
works on hard refresh.

### Environment variables

| Variable          | Where      | Example                                    |
| ----------------- | ---------- | ------------------------------------------ |
| `DATABASE_URL`    | Backend    | `sqlite:////data/app.db` (Fly volume)      |
| `ALLOWED_ORIGINS` | Backend    | `https://salary-management.vercel.app` (CSV) |
| `LOG_LEVEL`       | Backend    | `INFO` (default) / `DEBUG` for verbose runs |
| `LOG_SQL`         | Backend    | `false` (default); `true` to echo SQL as DEBUG |
| `VITE_API_URL`    | Frontend   | `https://salary-management.fly.dev`        |

## Manual smoke tests

See [`tasks/manual-test-scenarios.md`](./tasks/manual-test-scenarios.md)
for the canonical scenarios to run after deployment.
