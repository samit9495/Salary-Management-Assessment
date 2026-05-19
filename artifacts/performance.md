# Performance

Append a dated entry every time a perf-sensitive change lands. Keeps the optimization history visible to the assessor.

## 2026-05-20 — Seed 10k / 50k employees

- **Approach**: `random.Random(seed)`-driven generator with SQLAlchemy
  Core `insert()` in batches of 1000.
- **Host**: macOS 14 (Darwin 25.5.0), Apple Silicon, Python 3.12.12,
  SQLAlchemy 2.0.49, SQLite via stdlib `sqlite3`.
- **Result**:
  - `--count 10000 --seed 42 --reset` → **0.09 s** wall-clock,
    1.6 MB SQLite file.
  - `--count 50000 --seed 42 --reset` → **0.46 s** wall-clock,
    8.1 MB SQLite file.
  - In-memory perf test (`tests/seed/test_seed_perf.py`,
    `-m perf`) → **~0.12 s** for 10k rows.
- **Notes**:
  - Bulk path: `db.execute(insert(Employee), batch)` per 1000-row chunk.
    ORM `Session.add` was ~10x slower in a prior experiment because of
    per-row attribute instrumentation.
  - Deterministic via constructor-injected `random.Random` instance — no
    global `random.seed()`.
  - Did **not** drop indexes during insert; with this corpus size the
    index maintenance overhead is dwarfed by Python work.
  - PRAGMA `journal_mode` left at the SQLite default (delete) — switching
    to WAL was unnecessary at this volume.

## Template

```markdown
## YYYY-MM-DD — <what was measured>

- **Approach**: <one-line description>
- **Host**: <OS, CPU, Python/Node version>
- **Result**: <numbers with units>
- **Notes**: <alternatives tried, why they were rejected, any PRAGMA / config changes>
```

## Seed budget

Target: **10,000 employees seeded in under 5 seconds** on a typical dev laptop. See `.cursor/skills/incubyte-seed-performance/SKILL.md`.
