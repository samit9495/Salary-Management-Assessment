import logging
from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.services.employee_service import EmployeeService

SERVICE_LOGGER = "app.services.employee_service"


def _payload(**overrides: object) -> EmployeeCreate:
    base: dict[str, object] = {
        "full_name": "Jane Doe",
        "job_title": "Engineer",
        "country": "IN",
        "salary": Decimal("50000.00"),
    }
    base.update(overrides)
    return EmployeeCreate(**base)  # type: ignore[arg-type]


class TestEmployeeServiceCreate:
    def test_create_persists_employee_and_returns_with_id(self, db: Session) -> None:
        created = EmployeeService(db).create(_payload())

        assert created.id is not None
        assert created.full_name == "Jane Doe"
        assert db.get(Employee, created.id).salary == Decimal("50000.00")

    def test_create_logs_info_with_safe_identifiers(
        self, db: Session, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO, logger=SERVICE_LOGGER)

        created = EmployeeService(db).create(_payload(country="US"))

        records = [
            r
            for r in caplog.records
            if r.name == SERVICE_LOGGER and r.levelno == logging.INFO
        ]
        assert len(records) == 1
        record = records[0]
        assert record.event == "employee_created"
        assert record.employee_id == created.id
        assert record.country == "US"
        assert "email" not in record.__dict__
        assert "salary" not in record.__dict__


class TestEmployeeServiceUpdate:
    def test_update_logs_info_with_changed_field_names_only(
        self, db: Session, caplog: pytest.LogCaptureFixture
    ) -> None:
        existing = EmployeeService(db).create(_payload())
        caplog.clear()
        caplog.set_level(logging.INFO, logger=SERVICE_LOGGER)

        EmployeeService(db).update(
            existing.id,
            EmployeeUpdate(job_title="Senior Engineer", salary=Decimal("75000.00")),
        )

        records = [
            r
            for r in caplog.records
            if r.name == SERVICE_LOGGER and r.levelno == logging.INFO
        ]
        assert len(records) == 1
        record = records[0]
        assert record.event == "employee_updated"
        assert record.employee_id == existing.id
        assert sorted(record.fields_changed) == ["job_title", "salary"]


class TestEmployeeServiceDelete:
    def test_delete_logs_info_with_employee_id(
        self, db: Session, caplog: pytest.LogCaptureFixture
    ) -> None:
        existing = EmployeeService(db).create(_payload())
        caplog.clear()
        caplog.set_level(logging.INFO, logger=SERVICE_LOGGER)

        EmployeeService(db).delete(existing.id)

        records = [
            r
            for r in caplog.records
            if r.name == SERVICE_LOGGER and r.levelno == logging.INFO
        ]
        assert len(records) == 1
        record = records[0]
        assert record.event == "employee_deleted"
        assert record.employee_id == existing.id
