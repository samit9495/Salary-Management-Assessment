from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.employee import EmployeeRead
from app.schemas.insights import (
    CountryDistribution,
    CountryInsights,
    CountryTitleAverages,
    GlobalOverview,
    TitleCount,
    TopTitles,
)
from app.services.salary_insights_service import SalaryInsightsService

router = APIRouter(prefix="/insights", tags=["insights"])

CountryCode = Annotated[str, Path(min_length=2, max_length=2)]


@router.get("/by-country/{country}", response_model=CountryInsights)
def by_country(
    country: CountryCode,
    db: Session = Depends(get_db),
) -> CountryInsights:
    service = SalaryInsightsService(db)
    minimum, maximum = service.min_max_salary_by_country(country)
    return CountryInsights(
        country=country,
        average_salary=service.average_salary_by_country(country),
        min_salary=minimum,
        max_salary=maximum,
        employee_count=service.employee_count_by_country(country),
    )


@router.get("/by-country/{country}/by-title", response_model=CountryTitleAverages)
def by_country_and_title(
    country: CountryCode,
    db: Session = Depends(get_db),
) -> CountryTitleAverages:
    service = SalaryInsightsService(db)
    return CountryTitleAverages(
        country=country,
        averages=service.average_salary_by_country_and_title(country),
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
