# Analytics Strategy

> The set of macro-level HR insights that turn the salary list into a
> compensation analytics product: compa-ratio, range penetration,
> payroll burden, NTILE outlier detection. All built on SQLAlchemy
> window functions over SQLite. All driven by the
> [salary-mgmt bugs and analytics plan](../../.cursor/plans/salary-mgmt_bugs_and_analytics_2c8dd4b6.plan.md).

For the underlying schema see [backend-architecture.md](backend-architecture.md);
for the UI components that consume these endpoints see
[frontend-architecture.md](frontend-architecture.md) and
[ui-ux-decisions.md](ui-ux-decisions.md).

## The four metrics

| Metric | What it answers | Where it lives | Endpoint |
|---|---|---|---|
| **Compa-Ratio** | "How does this employee's salary compare to the average for their peer group (country + role)?" | `CompensationAnalysisService` | `GET /employees/compensation-analysis` |
| **Range Penetration** | "Where in the peer-group min↔max band does this salary sit?" | `CompensationAnalysisService` | `GET /employees/compensation-analysis` |
| **Payroll Burden** | "How is total payroll distributed across countries / roles?" | `SalaryInsightsService.payroll_by_*` | `GET /insights/payroll/by-country`, `/by-title` |
| **Outliers** | "Who's in the bottom 5% (retention risk) / top 5% (budget review) of their peer group?" | `SalaryInsightsService.salary_outliers` | `GET /insights/outliers?bucket=bottom\|top` |

## Why these four

The driving question from the
[driving-prompts archive](../prompts/driving-prompts.md):

> "Evolve the Insights page from basic averages into macro-level
> organizational compensation analytics."

These four metrics map directly to the four conversations an HR manager
actually has — pay equity (compa-ratio), career-progression planning
(range penetration), budget allocation (payroll burden), and outlier
review (NTILE). They are also computable from a single `Employee`
table without introducing benchmark data, equity bands, or external
salary surveys.

## Peer-group definition (the foundation)

Every metric partitions on the same peer group:

```sql
PARTITION BY country, LOWER(job_title)
```

- **Country**: the unit of regional pay parity.
- **`LOWER(job_title)`**: case-insensitive role grouping. HR may
  legitimately enter "Senior Engineer" vs "senior engineer" — see
  [tradeoffs-and-decisions.md](tradeoffs-and-decisions.md)
  §"Case-insensitive job-title normalization".

A single shared SQLAlchemy expression `title_canonical =
func.lower(Employee.job_title)` is the source of truth. It is reused
by `average_salary_by_country_and_title`, `top_titles_by_count`,
`payroll_by_title`, `salary_outliers`, and `CompensationAnalysisService`.

## Compa-Ratio + Range Penetration

```python
# app/services/compensation_analysis_service.py (paraphrased)
stmt = (
    select(
        Employee.id,
        Employee.salary,
        func.avg(Employee.salary).over(partition_by=(Employee.country, title_canonical)).label("avg_peer"),
        func.min(Employee.salary).over(partition_by=(Employee.country, title_canonical)).label("min_peer"),
        func.max(Employee.salary).over(partition_by=(Employee.country, title_canonical)).label("max_peer"),
    )
)
stmt = EmployeeRepository.apply_filters(stmt, country=country, q=q)
```

- **`compa_ratio = salary / avg_peer`** — three buckets in the UI:
  `< 0.8` underpaid, `[0.8, 1.2]` healthy, `> 1.2` highly compensated.
- **`range_penetration = (salary - min_peer) / (max_peer - min_peer)`**
  — 0% = at floor, 100% = at ceiling, undefined when min == max (UI
  shows a dash).

### Why a separate endpoint, not embedded

Documented in [tradeoffs-and-decisions.md](tradeoffs-and-decisions.md)
§"Compa-Ratio / Range Penetration as a separate endpoint". TL;DR:
list rows rarely change on every keystroke; peer aggregates do.
Separating lets the list endpoint stay slim and lets TanStack Query
cache the two responses independently. The compa endpoint applies
the **same filter chain** as `/employees` so the analyses map is
always scoped to what the table will render.

## Payroll Burden

```python
def payroll_by_country(self) -> PayrollResult:
    rows = self.db.execute(
        select(Employee.country, func.sum(Employee.salary))
        .group_by(Employee.country)
        .order_by(func.sum(Employee.salary).desc())
    ).all()
    return _payroll_response(rows)
```

- Returns `{total, entries: [{key, total, percentage}]}`.
- Percentages sum to 100 (locked by a unit test).
- Two endpoints: `/insights/payroll/by-country`, `/by-title`. The
  by-title variant uses `title_canonical` for grouping and the
  display-cased label for output.

The UI renders both stacked vertically in a `SummaryList` (per the
[insights polish plan](../../.cursor/plans/insights-polish-ux-pass_c3887b4e.plan.md)
— see [ui-ux-decisions.md](ui-ux-decisions.md) §"Payroll readability").

## NTILE Outliers

```python
def salary_outliers(self, bucket: Literal["bottom", "top"], min_group_size: int = 5, limit: int = 20):
    ntile_expr = func.ntile(20).over(
        partition_by=(Employee.country, title_canonical),
        order_by=Employee.salary,
    )
    target_bucket = 1 if bucket == "bottom" else 20
    # ... select with HAVING count(*) >= min_group_size
```

- `NTILE(20)` slices each peer group into twenty 5% buckets.
- `bucket=bottom` returns bucket 1 (retention risk); `bucket=top`
  returns bucket 20 (budget review).
- `min_group_size` (default 5) suppresses noise from one-person peer
  groups (a sole Designer in a country is not "an outlier").
- Why NTILE over absolute thresholds or z-scores: see
  [tradeoffs-and-decisions.md](tradeoffs-and-decisions.md)
  §"NTILE(20) for outlier detection".

## Data flow

```mermaid
flowchart LR
  EP[EmployeesPage] -->|"useEmployees(filters)"| RowsHook[useEmployees]
  EP -->|"useCompensationAnalysis(filters)"| AnalysisHook[useCompensationAnalysis]
  RowsHook -->|GET /employees| EmployeesRoute[employees.list_employees]
  AnalysisHook -->|GET /employees/compensation-analysis| AnalysisRoute[employees.compensation_analysis]
  EmployeesRoute --> EmployeeService
  AnalysisRoute --> CompService[CompensationAnalysisService]
  EmployeeService --> Repo[EmployeeRepository]
  CompService -->|window avg/min/max OVER (country, lower title)| DB[(SQLite)]
  Repo --> DB
  EP --> Join[EmployeesTable joins rows + analyses by id]
  Join --> Badge[CompaRatioBadge + RangePenetrationBar]

  IP[InsightsPage] -->|usePayrollBurden| PayrollHook[usePayrollBurden]
  IP -->|useOutliers| OutlierHook[useOutliers]
  PayrollHook -->|GET /insights/payroll/by-country / by-title| PayrollRoute[insights.payroll_*]
  OutlierHook -->|GET /insights/outliers| OutlierRoute[insights.outliers]
  PayrollRoute --> SalarySvc[SalaryInsightsService]
  OutlierRoute --> SalarySvc
```

## API surface added by analytics

| Method | Path | Returns |
|---|---|---|
| `GET` | `/employees/compensation-analysis?country=&q=` | `{ analyses: [EmployeeCompensationAnalysis] }` |
| `GET` | `/employees/countries?country=&q=` | `[{ code, count }]` (powers the searchable combobox) |
| `GET` | `/insights/payroll/by-country` | `{ total, entries: [{ key, total, percentage }] }` |
| `GET` | `/insights/payroll/by-title` | `{ total, entries: [{ key, total, percentage }] }` |
| `GET` | `/insights/outliers?bucket=bottom\|top&min_group_size=&limit=` | `[OutlierEntry]` |
| `GET` | `/insights/global` | `{ total_employees, average_salary, active_countries, active_titles }` |

All response shapes are `TypedDict` on the service side and Pydantic
`response_model` on the route side — the typed contract is end-to-end
(no `# type: ignore` survived the review-warnings pass).

## Performance posture

| Query | Complexity | At 10k | At 100k |
|---|---|---|---|
| Compa window | O(n) over filtered subset | < 5 ms | < 50 ms (window functions are O(n) per partition) |
| Payroll by country/title | O(n) aggregate + group | < 5 ms | < 50 ms |
| NTILE outliers | O(n log n) per partition | < 5 ms | < 100 ms |

At 1M+ rows, the `LOWER(job_title)` defeats the existing btree —
add a functional index on `lower(job_title)`. Documented in
[scalability-considerations.md](scalability-considerations.md).

## What this strategy deliberately does NOT include

- No materialized views, no caching. Aggregates are cheap; freshness
  matters.
- No client-side aggregation. The server does the grouping; the UI
  formats.
- No benchmark / equity-band data source. Out of scope for a
  single-tenant assessment tool. The `compa_ratio` could be
  re-anchored to an external "market median" later without touching
  the schema.
- No predictive metrics (attrition risk, salary forecast). YAGNI for
  the assessment.

## See also

- [backend-architecture.md](backend-architecture.md) — where these
  services live and how they're wired.
- [frontend-architecture.md](frontend-architecture.md) — the
  components that consume these endpoints.
- [ui-ux-decisions.md](ui-ux-decisions.md) — `AnalyticsSection`,
  `CompaRatioBadge`, `SummaryList`, tooltips.
- [tradeoffs-and-decisions.md](tradeoffs-and-decisions.md) — why a
  separate compa endpoint, why NTILE, why case-insensitive grouping.
