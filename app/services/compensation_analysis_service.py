from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, over, select
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.repositories.employee_repository import EmployeeRepository

RATIO_SCALE = Decimal("0.0001")


class CompensationAnalysisService:
    """Per-employee compensation analytics.

    Peer group is (country, lower(job_title)). For each employee we compute:

    - compa_ratio       = salary / avg(peer salary)        (1.0 = at midpoint)
    - range_penetration = (salary - min) / (max - min)     (0.0 = floor, 1.0 = ceiling;
                                                             0.0 when min == max)

    A single SQL window-function query keeps this O(n) regardless of
    peer-group count; no per-row Python aggregation.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def analyze(
        self,
        *,
        country: str | None = None,
        q: str | None = None,
    ) -> dict[int, dict[str, Decimal]]:
        # Local copy of the canonical (lowercased) job-title expression also
        # defined in app.services.salary_insights_service.title_canonical.
        # Kept local so the two services own their own SQL without an
        # implicit shared import.
        title_canonical = func.lower(Employee.job_title)
        partition = (Employee.country, title_canonical)

        peer_avg = over(func.avg(Employee.salary), partition_by=partition)
        peer_min = over(func.min(Employee.salary), partition_by=partition)
        peer_max = over(func.max(Employee.salary), partition_by=partition)

        stmt = select(
            Employee.id,
            Employee.salary,
            peer_avg.label("peer_avg"),
            peer_min.label("peer_min"),
            peer_max.label("peer_max"),
        )
        stmt = EmployeeRepository.apply_filters(stmt, country=country, q=q)

        result: dict[int, dict[str, Decimal]] = {}
        for emp_id, salary, peer_avg_val, peer_min_val, peer_max_val in self.db.execute(stmt):
            if peer_avg_val is None:
                continue
            avg = Decimal(peer_avg_val)
            mn = Decimal(peer_min_val)
            mx = Decimal(peer_max_val)
            spread = mx - mn
            penetration = (
                Decimal("0") if spread == 0 else (Decimal(salary) - mn) / spread
            )
            result[int(emp_id)] = {
                "peer_avg": avg.quantize(Decimal("0.01")),
                "peer_min": mn.quantize(Decimal("0.01")),
                "peer_max": mx.quantize(Decimal("0.01")),
                "compa_ratio": (Decimal(salary) / avg).quantize(RATIO_SCALE)
                if avg != 0
                else Decimal("0.0000"),
                "range_penetration": penetration.quantize(RATIO_SCALE),
            }
        return result

