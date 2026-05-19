# Tasks — Lessons Learned

Per `.cursor/rules/ai-workflow.mdc`, append a lesson when:

- A mistake was made and corrected
- An assumption turned out wrong
- A non-obvious pattern was discovered
- A gotcha cost extra time

If a lesson recurs, promote it to a `.cursor/rules/` entry so the rules enforce it.

## Lessons

### 2026-05-20 — SQLite `:memory:` + FastAPI TestClient needs StaticPool
**Context**: Phase 2.5 (POST /employees integration test) failed with
`sqlite3.OperationalError: no such table: employees` even though the
in-memory engine had `Base.metadata.create_all` called.
**Issue**: FastAPI's TestClient runs route handlers in a thread pool via
`run_in_threadpool`. SQLite's default `:memory:` database is per-connection;
each new connection (e.g. from a different thread) sees an empty database.
The test session's connection had the table; the handler's connection did
not.
**Fix/Insight**: Use `sqlalchemy.pool.StaticPool` so all connections share a
single in-memory database. Pattern:
`create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False},
poolclass=StaticPool, future=True)`. Promote to `.cursor/rules/` if it bites
again.

## Entry template

```
### YYYY-MM-DD — <short title>
**Context**: What was being done
**Issue**: What went wrong or was surprising
**Fix/Insight**: What to do differently next time
```
