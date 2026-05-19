from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.employee import Employee


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

    def list(self) -> list[Employee]:
        return list(self.db.scalars(select(Employee).order_by(Employee.id)))
