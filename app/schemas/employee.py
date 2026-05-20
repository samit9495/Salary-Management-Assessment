from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


def _uppercase_country(value: object) -> object:
    return value.upper() if isinstance(value, str) else value


CountryCode = Annotated[str, BeforeValidator(_uppercase_country)]
OptionalCountryCode = Annotated[str | None, BeforeValidator(_uppercase_country)]


class EmployeeBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=200, examples=["Jane Doe"])
    job_title: str = Field(min_length=1, max_length=100, examples=["Engineer"])
    country: CountryCode = Field(min_length=2, max_length=2, examples=["IN"])
    salary: Decimal = Field(ge=0, max_digits=12, decimal_places=2, examples=["50000.00"])
    email: str | None = Field(default=None, max_length=254, examples=["jane@example.com"])
    department: str | None = Field(default=None, max_length=80, examples=["Platform"])
    hire_date: date | None = Field(default=None, examples=["2024-01-15"])
    is_active: bool = Field(default=True)


class EmployeeCreate(EmployeeBase):
    """Payload used to create an employee."""


class EmployeeUpdate(BaseModel):
    """Partial update — all fields optional, validated when present."""

    full_name: str | None = Field(default=None, min_length=1, max_length=200)
    job_title: str | None = Field(default=None, min_length=1, max_length=100)
    country: OptionalCountryCode = Field(default=None, min_length=2, max_length=2)
    salary: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    email: str | None = Field(default=None, max_length=254)
    department: str | None = Field(default=None, max_length=80)
    hire_date: date | None = Field(default=None)
    is_active: bool | None = Field(default=None)


class EmployeeRead(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
