from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["employees"])


DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 500


@router.get("", response_model=list[EmployeeRead])
def list_employees(
    country: Annotated[str | None, Query(min_length=2, max_length=2)] = None,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_db),
) -> list[EmployeeRead]:
    employees = EmployeeService(db).list(country=country, limit=limit, offset=offset)
    return [EmployeeRead.model_validate(e) for e in employees]


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


@router.put("/{employee_id}", response_model=EmployeeRead)
def update_employee(
    employee_id: Annotated[int, Path(ge=1)],
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
) -> EmployeeRead:
    employee = EmployeeService(db).update(employee_id, payload)
    return EmployeeRead.model_validate(employee)
