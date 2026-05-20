from pathlib import Path

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.db.seed import run as seed_run
from app.models.employee import Employee


class TestSeedRun:
    def test_run_inserts_requested_count(self, db: Session) -> None:
        seed_run(db, count=100, rng_seed=1)
        total = db.execute(select(func.count(Employee.id))).scalar_one()
        assert total == 100

    def test_run_is_deterministic_with_same_seed(self, db: Session) -> None:
        seed_run(db, count=10, rng_seed=42)
        first = [
            (e.full_name, e.country, e.salary)
            for e in db.scalars(select(Employee).order_by(Employee.id))
        ]
        db.execute(delete(Employee))
        db.commit()

        seed_run(db, count=10, rng_seed=42)
        second = [
            (e.full_name, e.country, e.salary)
            for e in db.scalars(select(Employee).order_by(Employee.id))
        ]

        assert first == second

    def test_run_with_reset_clears_existing_rows(self, db: Session) -> None:
        seed_run(db, count=5, rng_seed=1)
        seed_run(db, count=3, rng_seed=1, reset=True)
        total = db.execute(select(func.count(Employee.id))).scalar_one()
        assert total == 3

    def test_run_raises_runtime_error_when_name_files_are_empty(
        self, db: Session, tmp_path: Path
    ) -> None:
        (tmp_path / "first_names.txt").write_text("", encoding="utf-8")
        (tmp_path / "last_names.txt").write_text("", encoding="utf-8")

        with pytest.raises(RuntimeError, match="name lists are empty"):
            seed_run(db, count=10, rng_seed=1, data_dir=tmp_path)
