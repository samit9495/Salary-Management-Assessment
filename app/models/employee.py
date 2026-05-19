from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    job_title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(254), unique=True, nullable=True)
    department: Mapped[str | None] = mapped_column(String(80), nullable=True)
    hire_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
