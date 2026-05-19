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
