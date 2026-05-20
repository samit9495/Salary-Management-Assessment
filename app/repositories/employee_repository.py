from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import InstrumentedAttribute, Session

from app.models.employee import Employee

SORTABLE_FIELDS: dict[str, InstrumentedAttribute] = {
    "id": Employee.id,
    "full_name": Employee.full_name,
    "job_title": Employee.job_title,
    "country": Employee.country,
    "salary": Employee.salary,
}


class EmployeeRepository:
    """Data access for the Employee aggregate.

    No business logic, no HTTP. Returns ORM instances or plain values.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, employee: Employee) -> Employee:
        self.db.add(employee)
        self.db.flush()
        return employee

    def get(self, employee_id: int) -> Employee | None:
        return self.db.get(Employee, employee_id)

    def list(
        self,
        *,
        country: str | None,
        q: str | None,
        sort: str | None,
        limit: int,
        offset: int,
    ) -> list[Employee]:
        stmt = self.apply_filters(select(Employee), country=country, q=q)
        order_column = _resolve_sort(sort)
        stmt = stmt.order_by(order_column).limit(limit).offset(offset)
        return list(self.db.scalars(stmt))

    def count(self, *, country: str | None, q: str | None) -> int:
        stmt = self.apply_filters(select(func.count(Employee.id)), country=country, q=q)
        return int(self.db.scalar(stmt) or 0)

    def distinct_countries(
        self, *, country: str | None = None, q: str | None = None
    ) -> list[tuple[str, int]]:
        stmt = self.apply_filters(
            select(Employee.country, func.count(Employee.id)),
            country=country,
            q=q,
        ).group_by(Employee.country).order_by(Employee.country)
        return [(code, int(count)) for code, count in self.db.execute(stmt).all()]

    @staticmethod
    def apply_filters(stmt, *, country: str | None, q: str | None):
        """Apply the shared (country, q-substring) filters to ``stmt``.

        Public because both :class:`EmployeeRepository` and the
        :class:`~app.services.compensation_analysis_service.CompensationAnalysisService`
        compose queries from the same filter contract.
        """
        if country is not None:
            stmt = stmt.where(Employee.country == country)
        if q:
            stmt = stmt.where(func.lower(Employee.full_name).like(f"%{q.lower()}%"))
        return stmt

    def delete(self, employee: Employee) -> None:
        self.db.delete(employee)
        self.db.flush()


def _resolve_sort(sort: str | None):
    if sort is None:
        return Employee.id
    direction_desc = sort.startswith("-")
    key = sort[1:] if direction_desc else sort
    column = SORTABLE_FIELDS[key]
    return column.desc() if direction_desc else column.asc()
