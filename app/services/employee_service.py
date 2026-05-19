import hashlib
import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateEmployeeEmail, EmployeeNotFound
from app.models.employee import Employee
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeUpdate

logger = logging.getLogger(__name__)


def _hash_email(email: str) -> str:
    """Return an 8-char SHA256 prefix of the email address.

    Used to log a stable identifier for a duplicate-email collision
    without putting raw PII in the log stream.
    """
    return hashlib.sha256(email.encode("utf-8")).hexdigest()[:8]


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
                logger.warning(
                    "duplicate_email",
                    extra={
                        "event": "duplicate_email",
                        "email_hash": _hash_email(payload.email),
                    },
                )
                raise DuplicateEmployeeEmail(payload.email) from exc
            raise
        self.db.refresh(employee)
        logger.info(
            "employee_created",
            extra={
                "event": "employee_created",
                "employee_id": employee.id,
                "country": employee.country,
            },
        )
        return employee

    def get(self, employee_id: int) -> Employee:
        employee = self.repo.get(employee_id)
        if employee is None:
            raise EmployeeNotFound(employee_id)
        return employee

    def list(
        self,
        *,
        country: str | None = None,
        q: str | None = None,
        sort: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Employee]:
        return self.repo.list(
            country=country, q=q, sort=sort, limit=limit, offset=offset
        )

    def count(self, *, country: str | None = None, q: str | None = None) -> int:
        return self.repo.count(country=country, q=q)

    def update(self, employee_id: int, payload: EmployeeUpdate) -> Employee:
        employee = self.get(employee_id)
        changed = payload.model_dump(exclude_unset=True)
        for field, value in changed.items():
            setattr(employee, field, value)
        self.db.commit()
        self.db.refresh(employee)
        logger.info(
            "employee_updated",
            extra={
                "event": "employee_updated",
                "employee_id": employee.id,
                "fields_changed": sorted(changed.keys()),
            },
        )
        return employee

    def delete(self, employee_id: int) -> None:
        employee = self.get(employee_id)
        self.repo.delete(employee)
        self.db.commit()
        logger.info(
            "employee_deleted",
            extra={
                "event": "employee_deleted",
                "employee_id": employee_id,
            },
        )
