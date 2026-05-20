from decimal import Decimal
from typing import Literal, TypedDict

from sqlalchemy import func, over, select
from sqlalchemy.orm import Session

from app.models.employee import Employee

NTILE_BUCKETS = 20
BOTTOM_BUCKET = 1
TOP_BUCKET = NTILE_BUCKETS
OutlierBucket = Literal["bottom", "top"]

SALARY_SCALE = Decimal("0.01")
PERCENTAGE_SCALE = Decimal("0.01")


class PayrollEntryResult(TypedDict):
    key: str
    total: Decimal
    percentage: Decimal


class PayrollResult(TypedDict):
    total: Decimal
    entries: list[PayrollEntryResult]


class GlobalOverviewResult(TypedDict):
    total_employees: int
    average_salary: Decimal
    active_countries: int
    active_titles: int


class OutlierResult(TypedDict):
    id: int
    full_name: str
    country: str
    job_title: str
    salary: Decimal
    bucket: int


# Canonical (case-insensitive) form of a job title used for grouping and
# aggregation. Storage keeps the original casing per row; insights collapse
# equivalent titles via this expression.
title_canonical = func.lower(Employee.job_title)


def display_title(canonical: str) -> str:
    """Human-readable form of a lowercase canonical title."""
    return canonical.title()


def _payroll_response(rows: list[tuple[str, Decimal]]) -> PayrollResult:
    total = sum((Decimal(t) for _, t in rows), Decimal("0"))
    entries: list[PayrollEntryResult] = []
    for key, raw_total in rows:
        amount = Decimal(raw_total).quantize(SALARY_SCALE)
        percentage = (
            (Decimal(raw_total) / total * Decimal("100")).quantize(PERCENTAGE_SCALE)
            if total > 0
            else Decimal("0.00")
        )
        entries.append({"key": key, "total": amount, "percentage": percentage})
    return {"total": total.quantize(SALARY_SCALE), "entries": entries}


class SalaryInsightsService:
    """Aggregate salary metrics for the Employee aggregate.

    Pure aggregations with SQL `func.*`; safe for empty data sets — every
    metric returns a sensible zero/empty value instead of raising.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def average_salary_by_country(self, country: str) -> Decimal:
        result = self.db.execute(
            select(func.avg(Employee.salary)).where(Employee.country == country)
        ).scalar_one()
        if result is None:
            return Decimal("0.00")
        return Decimal(result).quantize(SALARY_SCALE)

    def min_max_salary_by_country(self, country: str) -> tuple[Decimal, Decimal]:
        row = self.db.execute(
            select(func.min(Employee.salary), func.max(Employee.salary)).where(
                Employee.country == country
            )
        ).one()
        if row[0] is None:
            return (Decimal("0.00"), Decimal("0.00"))
        return (Decimal(row[0]).quantize(SALARY_SCALE), Decimal(row[1]).quantize(SALARY_SCALE))

    def average_salary_by_country_and_title(self, country: str) -> dict[str, Decimal]:
        rows = self.db.execute(
            select(title_canonical, func.avg(Employee.salary))
            .where(Employee.country == country)
            .group_by(title_canonical)
            .order_by(title_canonical)
        ).all()
        return {
            display_title(canonical): Decimal(avg).quantize(SALARY_SCALE)
            for canonical, avg in rows
        }

    def top_titles_by_count(self, *, limit: int) -> list[tuple[str, int]]:
        rows = self.db.execute(
            select(title_canonical, func.count(Employee.id).label("count"))
            .group_by(title_canonical)
            .order_by(func.count(Employee.id).desc(), title_canonical)
            .limit(limit)
        ).all()
        return [(display_title(canonical), int(count)) for canonical, count in rows]

    def employee_count_by_country(self, country: str) -> int:
        return int(
            self.db.execute(
                select(func.count(Employee.id)).where(Employee.country == country)
            ).scalar_one()
        )

    def employee_count_by_country_all(self) -> dict[str, int]:
        rows = self.db.execute(
            select(Employee.country, func.count(Employee.id))
            .group_by(Employee.country)
            .order_by(Employee.country)
        ).all()
        return {country: int(count) for country, count in rows}

    def recent_employees(self, *, limit: int) -> list[Employee]:
        return list(
            self.db.scalars(select(Employee).order_by(Employee.id.desc()).limit(limit))
        )

    def salary_outliers(
        self,
        *,
        bucket: OutlierBucket,
        min_group_size: int,
        limit: int,
    ) -> list[OutlierResult]:
        """Top or bottom 5% of salaries within each (country, title) peer group.

        Uses NTILE(20) so the threshold scales with the group's distribution.
        Groups smaller than ``min_group_size`` are skipped to avoid noise from
        tiny populations (where any single employee would land in bucket 1
        and bucket 20 simultaneously).
        """
        partition = (Employee.country, title_canonical)
        bucket_col = over(
            func.ntile(NTILE_BUCKETS),
            partition_by=partition,
            order_by=Employee.salary,
        ).label("bucket")
        group_size = over(func.count(Employee.id), partition_by=partition).label(
            "group_size"
        )

        subq = select(
            Employee.id,
            Employee.full_name,
            Employee.country,
            Employee.job_title,
            Employee.salary,
            bucket_col,
            group_size,
        ).subquery()

        target_bucket = BOTTOM_BUCKET if bucket == "bottom" else TOP_BUCKET
        salary_order = subq.c.salary.asc() if bucket == "bottom" else subq.c.salary.desc()

        stmt = (
            select(subq)
            .where(subq.c.bucket == target_bucket)
            .where(subq.c.group_size >= min_group_size)
            .order_by(salary_order, subq.c.id)
            .limit(limit)
        )

        return [
            OutlierResult(
                id=int(row.id),
                full_name=row.full_name,
                country=row.country,
                job_title=row.job_title,
                salary=Decimal(row.salary).quantize(SALARY_SCALE),
                bucket=int(row.bucket),
            )
            for row in self.db.execute(stmt)
        ]

    def payroll_by_country(self) -> PayrollResult:
        rows = self.db.execute(
            select(Employee.country, func.sum(Employee.salary))
            .group_by(Employee.country)
            .order_by(func.sum(Employee.salary).desc(), Employee.country)
        ).all()
        return _payroll_response([(country, total) for country, total in rows])

    def payroll_by_title(self) -> PayrollResult:
        rows = self.db.execute(
            select(title_canonical, func.sum(Employee.salary))
            .group_by(title_canonical)
            .order_by(func.sum(Employee.salary).desc(), title_canonical)
        ).all()
        return _payroll_response(
            [(display_title(canonical), total) for canonical, total in rows]
        )

    def global_overview(self) -> GlobalOverviewResult:
        row = self.db.execute(
            select(
                func.count(Employee.id),
                func.avg(Employee.salary),
                func.count(func.distinct(Employee.country)),
                func.count(func.distinct(title_canonical)),
            )
        ).one()
        total, avg, country_n, title_n = row
        return {
            "total_employees": int(total or 0),
            "average_salary": Decimal(avg).quantize(SALARY_SCALE)
            if avg is not None
            else Decimal("0.00"),
            "active_countries": int(country_n or 0),
            "active_titles": int(title_n or 0),
        }
