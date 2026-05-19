from sqlalchemy.orm import Session

from app.core.exceptions import EmployeeNotFound
from app.models.employee import Employee
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeCreate


class EmployeeService:
    """Use cases for the Employee aggregate.

    Constructor-injected Session; raises domain exceptions only.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = EmployeeRepository(db)

    def create(self, payload: EmployeeCreate) -> Employee:
        employee = Employee(**payload.model_dump())
        self.repo.add(employee)
        self.db.commit()
        self.db.refresh(employee)
        return employee

    def get(self, employee_id: int) -> Employee:
        employee = self.repo.get(employee_id)
        if employee is None:
            raise EmployeeNotFound(employee_id)
        return employee

    def list(self) -> list[Employee]:
        return self.repo.list()
