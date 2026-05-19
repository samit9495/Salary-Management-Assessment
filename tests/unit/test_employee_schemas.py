from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.employee import EmployeeCreate, EmployeeRead


def test_employee_create_accepts_valid_payload() -> None:
    payload = EmployeeCreate(
        full_name="Jane Doe",
        job_title="Engineer",
        country="IN",
        salary=Decimal("50000.00"),
    )
    assert payload.full_name == "Jane Doe"


def test_employee_create_rejects_negative_salary() -> None:
    with pytest.raises(ValidationError):
        EmployeeCreate(
            full_name="Jane Doe",
            job_title="Engineer",
            country="IN",
            salary=Decimal("-1"),
        )


def test_employee_create_rejects_non_iso2_country() -> None:
    with pytest.raises(ValidationError):
        EmployeeCreate(
            full_name="Jane Doe",
            job_title="Engineer",
            country="IND",
            salary=Decimal("50000"),
        )


def test_employee_create_rejects_blank_name() -> None:
    with pytest.raises(ValidationError):
        EmployeeCreate(
            full_name="",
            job_title="Engineer",
            country="IN",
            salary=Decimal("50000"),
        )


def test_employee_read_includes_id_from_orm_object() -> None:
    class Fake:
        id = 42
        full_name = "Jane Doe"
        job_title = "Engineer"
        country = "IN"
        salary = Decimal("50000.00")

    read = EmployeeRead.model_validate(Fake())
    assert read.id == 42
    assert read.full_name == "Jane Doe"
