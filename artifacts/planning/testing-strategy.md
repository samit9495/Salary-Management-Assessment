# Testing Strategy

> TDD is the workspace's primary discipline. Every behavior change in
> this repository was shipped as a `test:` commit followed by a
> `feat:` / `fix:` / `refactor:` commit. The
> [incubyte-tdd-discipline rule](../../.cursor/rules/incubyte-tdd-discipline.mdc)
> is the authoritative source; the
> [incubyte-tdd-loop skill](../../.cursor/skills/incubyte-tdd-loop/SKILL.md)
> is the one-screen recipe.

For the manual end-to-end scenarios used during the QA pass see
[../../tasks/manual-test-scenarios.md](../../tasks/manual-test-scenarios.md).

## Three Laws of TDD (Uncle Bob, encoded in the workspace)

1. You are not allowed to write any production code unless it is to
   make a failing unit test pass.
2. You are not allowed to write any more of a unit test than is
   sufficient to fail; and compilation failures are failures.
3. You are not allowed to write any more production code than is
   sufficient to pass the one currently failing unit test.

These laws are enforced by the always-apply rule and audited by the
[incubyte-code-reviewer agent](../../.cursor/agents/incubyte-code-reviewer.md)
on every major checkpoint.

## The loop

```
RED   →  write the smallest failing test (1 assertion). Run it. Confirm it fails.
COMMIT   test: <behavior>
GREEN →  write the minimum production code. Run all tests.
COMMIT   feat: <behavior>   (or fix:)
REFAC →  improve structure without changing behavior. Re-run all tests.
COMMIT   refactor: <what improved, why>   (only if anything changed)
```

One TDD step = one commit. **Never** combine test + impl + refactor.

## Backend (pytest)

| Layer | Tool | Lives in |
|---|---|---|
| Unit | pytest + in-memory SQLite | `tests/unit/` |
| Integration | pytest + `TestClient` + in-memory SQLite | `tests/integration/` |
| Seed | pytest + per-test SQLite + opt-in `-m perf` budget | `tests/seed/` |

Layout:

```
tests/
├── conftest.py                  shared fixtures: engine, db, client
├── unit/                        services, repositories, schemas, config
├── integration/                 routes via httpx TestClient, middleware
└── seed/                        seed determinism + perf budget
```

Fixtures (`tests/conftest.py`):

```python
@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)

@pytest.fixture
def db(engine):
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with Session() as s:
        yield s

@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

### Naming

- Files: `test_<module_under_test>.py`.
- Classes: `class TestSalaryInsightsService:`.
- Methods: `test_<action>_<condition>_<expected>`.

### Mock at the boundary

- Mock `time.time()`, `uuid.uuid4()`, the filesystem, the network.
- **Do not** mock `EmployeeRepository` when testing `EmployeeService`
  — use the real in-memory DB. The integration is the interesting
  part. This is the workspace rule, not a preference.

## Frontend (Vitest + RTL)

| Layer | Tool | Lives in |
|---|---|---|
| Pure helpers | Vitest | co-located `*.test.ts` |
| Components | Vitest + RTL + `userEvent` | co-located `*.test.tsx` |
| Hooks | Vitest + RTL `renderHook` + `QueryClientProvider` wrapper | co-located |
| Pages | Vitest + RTL + mocked services | `src/pages/*.test.tsx` |
| API client | Vitest + `fetch` mock | `src/lib/api.test.ts` |

**Behavioral, not snapshot.** Snapshot tests are forbidden by the
[incubyte-testing rule](../../.cursor/rules/incubyte-testing.mdc) —
they pin layout, not behavior.

```tsx
test("submitting the form posts an employee and shows the confirmation", async () => {
  render(<EmployeeForm onSubmit={mockSubmit} />)
  await userEvent.type(screen.getByLabelText(/full name/i), "Jane Doe")
  await userEvent.type(screen.getByLabelText(/salary/i), "50000")
  await userEvent.click(screen.getByRole("button", { name: /save/i }))
  expect(mockSubmit).toHaveBeenCalledWith(expect.objectContaining({ fullName: "Jane Doe" }))
})
```

jsdom polyfills (`ResizeObserver`, `PointerEvent`, `scrollIntoView`)
live in `src/test/setup.ts` so Radix Tooltip / cmdk work the same in
tests as in the browser.

## Characterization tests (refactor of untested code)

Per Sandro Mancuso: **you cannot change untested production code
safely**. If a refactor target lacks tests:

1. Write a characterization test that captures the *current*
   observable behavior, even if it looks wrong. Commit
   `test: characterize <function>`.
2. Refactor with that test as the safety net.
3. Fix any wrong behavior the test pinned down — separate RED → GREEN
   cycles, separate commits.

This produced two real bug-finds during the review-warnings pass:

- **`RequestContextMiddleware` skipped access log on 500.** A
  characterization test against a `/boom` route exposed the gap.
  Fixed by moving the log call to `finally`. See
  [tradeoffs-and-decisions.md](tradeoffs-and-decisions.md) §"Access
  log lives in finally".
- **`ALLOWED_ORIGINS` failed JSON-array parsing.** A new
  characterization test for the `Settings` validator exposed the
  pydantic-settings `NoDecode` interaction. Fixed with an explicit
  `json.loads()` branch.

## Determinism

- No `datetime.now()` in tests — inject a clock or use SQLAlchemy
  `server_default=func.now()` and assert the round-trip.
- No `random` without `random.Random(seed)`.
- No reliance on test execution order — `pytest-randomly` runs by
  default.
- No reliance on dict insertion order.

## Coverage gates

| Suite | Tool | Target |
|---|---|---|
| Backend | `pytest --cov=app --cov-report=term-missing` | ≥ 90% on changed modules; reports ≥ 99% overall |
| Frontend | `npm run test -- --coverage` | ≥ 80% on changed files (UI primitives floor below 90%) |

If coverage drops below the floor on a changed module, the
[incubyte-tdd-discipline rule](../../.cursor/rules/incubyte-tdd-discipline.mdc)
says: stop, add the RED tests, then continue.

## Speed targets

- Full backend suite: < 5 s after first run.
- Single unit test: < 100 ms (or < 500 ms for `TestClient` integration).
- Any slower test gets a `slow` mark or migrates to a `tests/seed/`
  perf-marked module.

## Manual end-to-end scenarios

The [incubyte-qa-automation agent](../../.cursor/agents/incubyte-qa-automation.md)
regenerates `tasks/manual-test-scenarios.md` after every major shipping
phase. The scenarios cover the workflows the automated suite cannot
fully exercise:

- Seed → list → create → edit → delete → insights happy paths.
- Country case-insensitivity end-to-end (Insights page hits the same
  data as Employees page when typing `IN` vs `in`).
- Pagination "of N" updates as filters change.
- Compa-ratio badges + payroll burden + outlier tables render after a
  cold reload.
- Logging: `X-Request-ID` returns on every response (incl. 500 paths
  from a forced `/boom` route).

## Running the suites

```bash
# Backend
pytest -v
pytest --cov=app --cov-report=term-missing
pytest tests/unit/test_salary_insights_service.py -v
pytest -m perf            # opt-in seed perf budget

# Frontend
cd frontend
npm run test
npm run test -- --coverage
```

## See also

- [implementation-phases.md](implementation-phases.md) — per-phase
  micro-task tables, each row is one TDD pair.
- [seed-performance-strategy.md](seed-performance-strategy.md) — the
  perf-budget test and its measurement protocol.
- [ai-assisted-workflow.md](ai-assisted-workflow.md) — how Cursor's
  rules and the QA-automation agent keep TDD discipline visible in
  every session.
- [../../tasks/manual-test-scenarios.md](../../tasks/manual-test-scenarios.md)
  — the maintained list of end-to-end smoke scenarios.
