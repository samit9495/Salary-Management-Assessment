from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.services.salary_insights_service import SalaryInsightsService


class TestAverageSalaryByCountry:
    def test_returns_zero_when_no_employees(self, db: Session) -> None:
        service = SalaryInsightsService(db)
        assert service.average_salary_by_country("IN") == Decimal("0.00")

    def test_returns_arithmetic_mean_with_two_decimal_quantization(
        self, db: Session
    ) -> None:
        for amount in (Decimal("100"), Decimal("200"), Decimal("303")):
            db.add(
                Employee(
                    full_name="X",
                    job_title="E",
                    country="IN",
                    salary=amount,
                )
            )
        db.commit()

        service = SalaryInsightsService(db)
        assert service.average_salary_by_country("IN") == Decimal("201.00")

    def test_excludes_other_countries(self, db: Session) -> None:
        db.add(Employee(full_name="A", job_title="E", country="IN", salary=Decimal("500")))
        db.add(Employee(full_name="B", job_title="E", country="US", salary=Decimal("9999")))
        db.commit()

        service = SalaryInsightsService(db)
        assert service.average_salary_by_country("IN") == Decimal("500.00")


class TestMinMaxSalaryByCountry:
    def test_min_max_return_zero_zero_when_no_employees(self, db: Session) -> None:
        service = SalaryInsightsService(db)
        assert service.min_max_salary_by_country("IN") == (Decimal("0.00"), Decimal("0.00"))

    def test_min_max_returns_bounds(self, db: Session) -> None:
        for amount in (Decimal("100"), Decimal("500"), Decimal("250")):
            db.add(Employee(full_name="X", job_title="E", country="IN", salary=amount))
        db.commit()

        service = SalaryInsightsService(db)
        assert service.min_max_salary_by_country("IN") == (
            Decimal("100.00"),
            Decimal("500.00"),
        )


class TestAverageSalaryByCountryAndTitle:
    def test_returns_empty_dict_when_country_has_no_employees(self, db: Session) -> None:
        assert SalaryInsightsService(db).average_salary_by_country_and_title("IN") == {}

    def test_groups_by_job_title_and_quantizes(self, db: Session) -> None:
        rows = [
            ("Engineer", Decimal("100")),
            ("Engineer", Decimal("200")),
            ("Manager", Decimal("500")),
        ]
        for title, salary in rows:
            db.add(Employee(full_name="X", job_title=title, country="IN", salary=salary))
        db.commit()

        result = SalaryInsightsService(db).average_salary_by_country_and_title("IN")

        assert result == {"Engineer": Decimal("150.00"), "Manager": Decimal("500.00")}

    def test_collapses_case_variants_into_single_bucket(self, db: Session) -> None:
        rows = [
            ("Engineer", Decimal("100")),
            ("engineer", Decimal("200")),
            ("ENGINEER", Decimal("300")),
        ]
        for title, salary in rows:
            db.add(Employee(full_name="X", job_title=title, country="IN", salary=salary))
        db.commit()

        result = SalaryInsightsService(db).average_salary_by_country_and_title("IN")

        assert result == {"Engineer": Decimal("200.00")}


class TestGlobalOverview:
    def test_returns_zeros_when_no_employees(self, db: Session) -> None:
        overview = SalaryInsightsService(db).global_overview()
        assert overview == {
            "total_employees": 0,
            "average_salary": Decimal("0.00"),
            "active_countries": 0,
            "active_titles": 0,
        }

    def test_aggregates_across_countries(self, db: Session) -> None:
        rows = [
            ("IN", "Engineer", Decimal("100")),
            ("IN", "Engineer", Decimal("200")),
            ("US", "Manager", Decimal("600")),
        ]
        for country, title, salary in rows:
            db.add(
                Employee(
                    full_name="X",
                    job_title=title,
                    country=country,
                    salary=salary,
                )
            )
        db.commit()

        overview = SalaryInsightsService(db).global_overview()
        assert overview == {
            "total_employees": 3,
            "average_salary": Decimal("300.00"),
            "active_countries": 2,
            "active_titles": 2,
        }


class TestCountryDistribution:
    def test_returns_count_per_country(self, db: Session) -> None:
        for country in ("IN", "IN", "US"):
            db.add(
                Employee(
                    full_name="X",
                    job_title="E",
                    country=country,
                    salary=Decimal("1"),
                )
            )
        db.commit()

        distribution = SalaryInsightsService(db).employee_count_by_country_all()
        assert distribution == {"IN": 2, "US": 1}


class TestSalaryOutliers:
    def _seed(self, db: Session) -> None:
        # Engineers in IN: salaries 1..20 → 20 buckets, one per salary
        for i in range(1, 21):
            db.add(
                Employee(
                    full_name=f"IN-Eng-{i}",
                    job_title="Engineer",
                    country="IN",
                    salary=Decimal(i),
                )
            )
        # Tiny group: only 2 designers in US — should be filtered by min_group_size
        for i in range(1, 3):
            db.add(
                Employee(
                    full_name=f"US-Des-{i}",
                    job_title="Designer",
                    country="US",
                    salary=Decimal(i * 100),
                )
            )
        db.commit()

    def test_returns_empty_when_no_employees(self, db: Session) -> None:
        result = SalaryInsightsService(db).salary_outliers(
            bucket="bottom", min_group_size=5, limit=10
        )
        assert result == []

    def test_bottom_returns_lowest_bucket_in_peer_group(self, db: Session) -> None:
        self._seed(db)

        result = SalaryInsightsService(db).salary_outliers(
            bucket="bottom", min_group_size=5, limit=10
        )

        names = [e["full_name"] for e in result]
        # IN engineers with salary 1 falls in bucket 1 of NTILE(20)
        assert "IN-Eng-1" in names
        # Tiny US designer group is skipped
        assert all("US-Des" not in n for n in names)

    def test_top_returns_highest_bucket_in_peer_group(self, db: Session) -> None:
        self._seed(db)

        result = SalaryInsightsService(db).salary_outliers(
            bucket="top", min_group_size=5, limit=10
        )

        names = [e["full_name"] for e in result]
        assert "IN-Eng-20" in names
        assert all("US-Des" not in n for n in names)


class TestPayrollBurden:
    def test_returns_empty_when_no_employees(self, db: Session) -> None:
        assert SalaryInsightsService(db).payroll_by_country() == {
            "total": Decimal("0.00"),
            "entries": [],
        }

    def test_payroll_by_country_returns_totals_and_percentages(self, db: Session) -> None:
        rows = [
            ("IN", Decimal("60")),
            ("IN", Decimal("40")),
            ("US", Decimal("300")),
        ]
        for country, salary in rows:
            db.add(Employee(full_name="X", job_title="E", country=country, salary=salary))
        db.commit()

        result = SalaryInsightsService(db).payroll_by_country()

        assert result["total"] == Decimal("400.00")
        assert result["entries"] == [
            {"key": "US", "total": Decimal("300.00"), "percentage": Decimal("75.00")},
            {"key": "IN", "total": Decimal("100.00"), "percentage": Decimal("25.00")},
        ]

    def test_payroll_by_title_groups_case_insensitively(self, db: Session) -> None:
        rows = [
            ("Engineer", Decimal("50")),
            ("engineer", Decimal("50")),
            ("Manager", Decimal("100")),
        ]
        for title, salary in rows:
            db.add(Employee(full_name="X", job_title=title, country="IN", salary=salary))
        db.commit()

        result = SalaryInsightsService(db).payroll_by_title()

        assert result["total"] == Decimal("200.00")
        assert result["entries"] == [
            {"key": "Engineer", "total": Decimal("100.00"), "percentage": Decimal("50.00")},
            {"key": "Manager", "total": Decimal("100.00"), "percentage": Decimal("50.00")},
        ]


class TestRecentEmployees:
    def test_returns_most_recent_by_id_descending(self, db: Session) -> None:
        for name in ("A", "B", "C", "D"):
            db.add(Employee(full_name=name, job_title="E", country="IN", salary=Decimal("1")))
        db.commit()

        recent = SalaryInsightsService(db).recent_employees(limit=2)
        assert [e.full_name for e in recent] == ["D", "C"]


class TestTopTitlesByEmployeeCount:
    def test_returns_empty_list_when_no_employees(self, db: Session) -> None:
        assert SalaryInsightsService(db).top_titles_by_count(limit=5) == []

    def test_returns_titles_ordered_by_count_descending(self, db: Session) -> None:
        rows = [
            ("Engineer", 3),
            ("Manager", 2),
            ("Designer", 1),
        ]
        for title, count in rows:
            for _ in range(count):
                db.add(
                    Employee(
                        full_name="X",
                        job_title=title,
                        country="IN",
                        salary=Decimal("100"),
                    )
                )
        db.commit()

        result = SalaryInsightsService(db).top_titles_by_count(limit=2)

        assert result == [("Engineer", 3), ("Manager", 2)]

    def test_collapses_case_variants(self, db: Session) -> None:
        for title in ("Engineer", "engineer", "ENGINEER", "Manager"):
            db.add(Employee(full_name="X", job_title=title, country="IN", salary=Decimal("1")))
        db.commit()

        result = SalaryInsightsService(db).top_titles_by_count(limit=5)

        assert result == [("Engineer", 3), ("Manager", 1)]
