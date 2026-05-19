from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.employee import EmployeeCreate, EmployeeRead
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=list[EmployeeRead])
def list_employees(
    db: Session = Depends(get_db),
) -> list[EmployeeRead]:
    return [EmployeeRead.model_validate(e) for e in EmployeeService(db).list()]


@router.post("", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
) -> EmployeeRead:
    employee = EmployeeService(db).create(payload)
    return EmployeeRead.model_validate(employee)


@router.get("/{employee_id}", response_model=EmployeeRead)
def get_employee(
    employee_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
) -> EmployeeRead:
    employee = EmployeeService(db).get(employee_id)
    return EmployeeRead.model_validate(employee)
