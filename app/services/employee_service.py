from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateEmployeeEmail, EmployeeNotFound
from app.models.employee import Employee
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    """Use cases for the Employee aggregate.

    Constructor-injected Session; raises domain exceptions only.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = EmployeeRepository(db)

    def create(self, payload: EmployeeCreate) -> Employee:
        employee = Employee(**payload.model_dump())
        try:
            self.repo.add(employee)
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            if payload.email is not None and "email" in str(exc.orig).lower():
                raise DuplicateEmployeeEmail(payload.email) from exc
            raise
        self.db.refresh(employee)
        return employee

    def get(self, employee_id: int) -> Employee:
        employee = self.repo.get(employee_id)
        if employee is None:
            raise EmployeeNotFound(employee_id)
        return employee

    def list(
        self, *, country: str | None = None, limit: int = 50, offset: int = 0
    ) -> list[Employee]:
        return self.repo.list(country=country, limit=limit, offset=offset)

    def update(self, employee_id: int, payload: EmployeeUpdate) -> Employee:
        employee = self.get(employee_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(employee, field, value)
        self.db.commit()
        self.db.refresh(employee)
        return employee

    def delete(self, employee_id: int) -> None:
        employee = self.get(employee_id)
        self.repo.delete(employee)
        self.db.commit()
