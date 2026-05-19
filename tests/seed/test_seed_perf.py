import time

import pytest
from sqlalchemy.orm import Session

from app.db.seed import run as seed_run

PERF_BUDGET_SECONDS = 10.0
SEED_COUNT = 10_000


@pytest.mark.perf
def test_seed_10000_completes_within_budget(db: Session) -> None:
    started = time.perf_counter()
    seed_run(db, count=SEED_COUNT, rng_seed=42)
    elapsed = time.perf_counter() - started

    assert elapsed < PERF_BUDGET_SECONDS, f"seed took {elapsed:.2f}s, budget {PERF_BUDGET_SECONDS}s"
