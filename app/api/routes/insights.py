from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import (
    OutlierEntry,
    OutlierResponse,
    PayrollBurdenResponse,
    PayrollEntry,
)
from app.schemas.employee import EmployeeRead
from app.schemas.insights import (
    CountryDistribution,
    CountryInsights,
    CountryTitleAverages,
    GlobalOverview,
    TitleCount,
    TopTitles,
)
from app.services.salary_insights_service import (
    PayrollResult,
    SalaryInsightsService,
)


def _payroll_payload(payroll: PayrollResult) -> PayrollBurdenResponse:
    return PayrollBurdenResponse(
        total=payroll["total"],
        entries=[PayrollEntry(**entry) for entry in payroll["entries"]],
    )

router = APIRouter(prefix="/insights", tags=["insights"])

CountryCode = Annotated[str, Path(min_length=2, max_length=2)]


@router.get("/by-country/{country}", response_model=CountryInsights)
def by_country(
    country: CountryCode,
    db: Session = Depends(get_db),
) -> CountryInsights:
    canonical = country.upper()
    service = SalaryInsightsService(db)
    minimum, maximum = service.min_max_salary_by_country(canonical)
    return CountryInsights(
        country=canonical,
        average_salary=service.average_salary_by_country(canonical),
        min_salary=minimum,
        max_salary=maximum,
        employee_count=service.employee_count_by_country(canonical),
    )


@router.get("/by-country/{country}/by-title", response_model=CountryTitleAverages)
def by_country_and_title(
    country: CountryCode,
    db: Session = Depends(get_db),
) -> CountryTitleAverages:
    canonical = country.upper()
    service = SalaryInsightsService(db)
    return CountryTitleAverages(
        country=canonical,
        averages=service.average_salary_by_country_and_title(canonical),
    )


@router.get("/top-titles", response_model=TopTitles)
def top_titles(
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    db: Session = Depends(get_db),
) -> TopTitles:
    rows = SalaryInsightsService(db).top_titles_by_count(limit=limit)
    return TopTitles(titles=[TitleCount(title=t, count=c) for t, c in rows])


@router.get("/overview", response_model=GlobalOverview)
def overview(db: Session = Depends(get_db)) -> GlobalOverview:
    return GlobalOverview(**SalaryInsightsService(db).global_overview())


@router.get("/recent", response_model=list[EmployeeRead])
def recent(
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    db: Session = Depends(get_db),
) -> list[EmployeeRead]:
    employees = SalaryInsightsService(db).recent_employees(limit=limit)
    return [EmployeeRead.model_validate(e) for e in employees]


@router.get("/distribution", response_model=CountryDistribution)
def distribution(db: Session = Depends(get_db)) -> CountryDistribution:
    return CountryDistribution(counts=SalaryInsightsService(db).employee_count_by_country_all())


@router.get("/payroll/by-country", response_model=PayrollBurdenResponse)
def payroll_by_country(db: Session = Depends(get_db)) -> PayrollBurdenResponse:
    return _payroll_payload(SalaryInsightsService(db).payroll_by_country())


@router.get("/payroll/by-title", response_model=PayrollBurdenResponse)
def payroll_by_title(db: Session = Depends(get_db)) -> PayrollBurdenResponse:
    return _payroll_payload(SalaryInsightsService(db).payroll_by_title())


@router.get("/outliers", response_model=OutlierResponse)
def outliers(
    bucket: Annotated[Literal["bottom", "top"], Query()] = "bottom",
    min_group_size: Annotated[int, Query(ge=2, le=200)] = 5,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    db: Session = Depends(get_db),
) -> OutlierResponse:
    rows = SalaryInsightsService(db).salary_outliers(
        bucket=bucket, min_group_size=min_group_size, limit=limit
    )
    return OutlierResponse(
        bucket=bucket,
        entries=[OutlierEntry(**row) for row in rows],
    )
