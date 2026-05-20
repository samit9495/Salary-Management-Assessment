from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.employee_repository import SORTABLE_FIELDS
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate
from app.services.employee_service import EmployeeService

_ALLOWED_SORT_VALUES = sorted(
    [k for k in SORTABLE_FIELDS] + [f"-{k}" for k in SORTABLE_FIELDS]
)
_SORT_PATTERN = "^(-)?(" + "|".join(SORTABLE_FIELDS.keys()) + ")$"

router = APIRouter(prefix="/employees", tags=["employees"])


DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 500


@router.get("", response_model=list[EmployeeRead])
def list_employees(
    response: Response,
    country: Annotated[str | None, Query(min_length=2, max_length=2)] = None,
    q: Annotated[str | None, Query(max_length=100)] = None,
    sort: Annotated[str | None, Query(pattern=_SORT_PATTERN)] = None,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_db),
) -> list[EmployeeRead]:
    canonical_country = country.upper() if country else None
    service = EmployeeService(db)
    employees = service.list(
        country=canonical_country, q=q, sort=sort, limit=limit, offset=offset
    )
    response.headers["X-Total-Count"] = str(
        service.count(country=canonical_country, q=q)
    )
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


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: Annotated[int, Path(ge=1)],
    db: Session = Depends(get_db),
) -> Response:
    EmployeeService(db).delete(employee_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
