from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CountryInsights(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    country: str
    average_salary: Decimal
    min_salary: Decimal
    max_salary: Decimal
    employee_count: int


class CountryTitleAverages(BaseModel):
    country: str
    averages: dict[str, Decimal]


class TitleCount(BaseModel):
    title: str
    count: int


class TopTitles(BaseModel):
    titles: list[TitleCount] = Field(default_factory=list)


class GlobalOverview(BaseModel):
    total_employees: int
    average_salary: Decimal
    active_countries: int
    active_titles: int


class CountryDistribution(BaseModel):
    counts: dict[str, int]
