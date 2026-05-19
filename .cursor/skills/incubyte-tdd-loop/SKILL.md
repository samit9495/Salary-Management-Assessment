---
name: incubyte-tdd-loop
description: The one-screen Red-Green-Refactor-Commit recipe. Read this at the start of every behavior change. The default workflow for the Incubyte assessment.
---

# Incubyte TDD Loop

## Trigger

Use when asked to: `TDD: <behavior>`, `RED:`, `GREEN:`, `REFACTOR:`, or any prompt that requests new behavior, a bug fix, or a refactor. **If you are about to write production code, run this skill first.**

## Context

The Incubyte assessment is graded on the visible TDD evolution in `git log`. This skill produces a commit history that looks like:

```
abc1234 test: average salary by country returns 0 when no employees
def5678 feat: implement average_salary_by_country returning Decimal
9abcde0 refactor: extract _aggregate_salaries helper
```

Every step gets its own commit. The assessor can replay the design decisions.

## The loop

### Step 1 — RED: write the smallest failing test

Pick the next observable behavior. Write the test that proves it does not work yet.

```python
# tests/unit/test_salary_insights_service.py
def test_average_salary_by_country_returns_zero_when_no_employees(db):
    service = SalaryInsightsService(db)
    assert service.average_salary_by_country("IN") == Decimal("0.00")
```

Constraints:

- One assertion (or one tightly coupled set of assertions about the same fact).
- The test must fail because the behavior is missing, not because of a typo or import error.
- If it fails to compile / import — that **counts as a failure** per the second law of TDD. Move on once compilation alone produces a clear failure.

### Step 2 — Run it and confirm it fails

```bash
pytest tests/unit/test_salary_insights_service.py::test_average_salary_by_country_returns_zero_when_no_employees -v
```

Paste the failure into the chat. If it does not fail — you did not understand the behavior. Start over.

### Step 3 — Commit the RED

```bash
git add tests/unit/test_salary_insights_service.py
git commit -m "test: average salary by country returns 0 when no employees"
```

The commit message uses the `test:` prefix. The body (optional) can name the file and the behavior in one line.

### Step 4 — GREEN: minimum code to pass

Write the **least** production code that makes the test pass. No more.

```python
# app/services/salary_insights_service.py
from decimal import Decimal

class SalaryInsightsService:
    def __init__(self, db):
        self.db = db

    def average_salary_by_country(self, country: str) -> Decimal:
        return Decimal("0.00")
```

Yes, this is "wrong" in the long run. It will get fixed in the next RED step. The Third Law forbids writing more.

### Step 5 — Run all tests; confirm green

```bash
pytest -v
```

Paste the pass. If anything else broke, fix the smallest possible thing or revert.

### Step 6 — Commit the GREEN

```bash
git add app/services/salary_insights_service.py
git commit -m "feat: implement average_salary_by_country returning Decimal"
```

`feat:` for new behavior, `fix:` for a regression test that proved a bug, `chore:` only if the production change is purely scaffolding.

### Step 7 — REFACTOR (optional, but encouraged)

If the code or the test can be cleaner without changing behavior:

- Rename variables.
- Extract helpers.
- Push behavior onto the right object.
- Eliminate duplication that now exists between this and previous code.

Re-run all tests after every micro-step. If anything breaks, undo and try a smaller refactor. If nothing changed: skip this step, no commit.

### Step 8 — Commit the REFACTOR

```bash
git add -A
git commit -m "refactor: extract _aggregate_salaries helper"
```

`refactor:` commits never add tests and never change behavior.

### Step 9 — Artifact audit (60-second check)

Before looping back, ask whether the commit(s) you just made introduced any of these. Most loops produce **none** — that is correct. Spam in `artifacts/` is worse than gaps.

| Trigger in the commit | Artifact to update |
|-----------------------|--------------------|
| A design decision picked among real alternatives | `artifacts/tradeoffs.md` |
| A perf measurement, or any `perf:` commit | `artifacts/performance.md` |
| A notable AI prompt that shipped (Stitch MCP, council outcome) | new file under `artifacts/prompts/` |
| A cross-cutting structural change | diagram or note in `artifacts/architecture/` |
| The start of a major feature | planning note in `artifacts/planning/` |

If yes, append the entry using the templates in `artifacts/README.md` and commit:

```bash
git add artifacts/
git commit -m "docs(artifacts): <one-line summary>"
```

If no, continue. The reminder hook at `scripts/git-hooks/post-commit` (see `scripts/git-hooks/README.md` for one-time install) prints a nag whenever the commit subject matches `^perf:`, `^docs(stitch):`, contains `!:` (breaking), or whose body opens with `tradeoff:` / `decision:` / `considered:`.

Commits that almost never need an artifact entry: `test:`, plain `feat:` for a small behavior, `refactor:`, `chore:`, `style:`.

### Step 10 — Loop back

Pick the next behavior. Often it is the case the current "Decimal(0)" hard-code does not match the next test, so the next RED step will be:

```python
def test_average_salary_by_country_computes_mean(db):
    add_employee(db, country="IN", salary=Decimal("100"))
    add_employee(db, country="IN", salary=Decimal("300"))
    add_employee(db, country="US", salary=Decimal("999"))  # excluded
    assert SalaryInsightsService(db).average_salary_by_country("IN") == Decimal("200.00")
```

…and so on.

## Anti-patterns this skill prevents

- Writing the implementation first and then "adding tests" — the test was not failing for the right reason.
- Bundling test + implementation + refactor into one commit — the assessor cannot read the design decisions.
- Writing five tests up-front for a feature — overcommits to a design you have not validated.
- Refactoring while a test is red — you no longer have a safety net.

## Cross-references

- `.cursor/rules/incubyte-tdd-discipline.mdc` — the Three Laws and the "what counts as a test" table.
- `.cursor/rules/incubyte-commit-hygiene.mdc` — message conventions.
- `.cursor/rules/incubyte-testing.mdc` — pytest layout and fixtures.
- `.cursor/agents/incubyte-code-reviewer.md` — the git log audit checklist that this skill produces compliant input for.
