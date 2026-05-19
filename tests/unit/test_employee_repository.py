from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.repositories.employee_repository import EmployeeRepository


class TestEmployeeRepository:
    def test_add_persists_employee_and_returns_with_id(self, db: Session) -> None:
        repo = EmployeeRepository(db)
        employee = Employee(
            full_name="Jane Doe",
            job_title="Engineer",
            country="IN",
            salary=Decimal("50000"),
        )
        saved = repo.add(employee)

        assert saved.id is not None
        assert db.get(Employee, saved.id) is saved

    def test_get_returns_employee_when_present(self, db: Session) -> None:
        repo = EmployeeRepository(db)
        employee = repo.add(
            Employee(full_name="A", job_title="E", country="IN", salary=Decimal("1"))
        )
        db.commit()

        assert repo.get(employee.id).id == employee.id

    def test_get_returns_none_when_missing(self, db: Session) -> None:
        repo = EmployeeRepository(db)
        assert repo.get(9999) is None
