from decimal import Decimal

from fastapi.testclient import TestClient


def _post(client: TestClient, **overrides: object) -> None:
    base = {
        "full_name": "X",
        "job_title": "Engineer",
        "country": "IN",
        "salary": "100.00",
    }
    base.update(overrides)
    client.post("/employees", json=base)


class TestInsightsByCountry:
    def test_empty_country_returns_zero_values(self, client: TestClient) -> None:
        response = client.get("/insights/by-country/IN")

        assert response.status_code == 200
        body = response.json()
        assert body == {
            "country": "IN",
            "average_salary": "0.00",
            "min_salary": "0.00",
            "max_salary": "0.00",
            "employee_count": 0,
        }

    def test_returns_min_max_avg_and_count(self, client: TestClient) -> None:
        _post(client, salary="100.00")
        _post(client, salary="300.00")
        _post(client, salary="500.00")

        body = client.get("/insights/by-country/IN").json()

        assert body["average_salary"] == "300.00"
        assert body["min_salary"] == "100.00"
        assert body["max_salary"] == "500.00"
        assert body["employee_count"] == 3


class TestInsightsByCountryAndTitle:
    def test_returns_breakdown_by_title(self, client: TestClient) -> None:
        _post(client, job_title="Engineer", salary="100")
        _post(client, job_title="Engineer", salary="200")
        _post(client, job_title="Manager", salary="500")

        body = client.get("/insights/by-country/IN/by-title").json()

        assert body == {
            "country": "IN",
            "averages": {"Engineer": "150.00", "Manager": "500.00"},
        }


class TestTopTitlesEndpoint:
    def test_returns_top_titles_ordered_by_count(self, client: TestClient) -> None:
        for _ in range(3):
            _post(client, job_title="Engineer")
        for _ in range(2):
            _post(client, job_title="Manager")
        _post(client, job_title="Designer")

        body = client.get("/insights/top-titles", params={"limit": 2}).json()

        assert body == {
            "titles": [
                {"title": "Engineer", "count": 3},
                {"title": "Manager", "count": 2},
            ]
        }


class TestInsightsCountryCaseInsensitive:
    def test_lowercase_path_matches_uppercase(self, client: TestClient) -> None:
        _post(client, country="IN", salary="100")

        lower_body = client.get("/insights/by-country/in").json()
        upper_body = client.get("/insights/by-country/IN").json()

        assert lower_body == upper_body
        assert lower_body["employee_count"] == 1

    def test_lowercase_path_returns_canonical_country(self, client: TestClient) -> None:
        _post(client, country="IN", salary="100")
        body = client.get("/insights/by-country/in").json()
        assert body["country"] == "IN"


class TestEmployeesCountryQueryCaseInsensitive:
    def test_lowercase_country_filter_matches_uppercase(self, client: TestClient) -> None:
        _post(client, country="IN")
        _post(client, country="US")

        body = client.get("/employees", params={"country": "in"}).json()

        assert [row["country"] for row in body] == ["IN"]


class TestGlobalOverviewEndpoint:
    def test_empty_db_returns_zero_overview(self, client: TestClient) -> None:
        body = client.get("/insights/overview").json()
        assert body == {
            "total_employees": 0,
            "average_salary": "0.00",
            "active_countries": 0,
            "active_titles": 0,
        }

    def test_aggregates_across_countries(self, client: TestClient) -> None:
        _post(client, country="IN", job_title="Engineer", salary="100")
        _post(client, country="US", job_title="Manager", salary="500")

        body = client.get("/insights/overview").json()
        assert body["total_employees"] == 2
        assert body["average_salary"] == "300.00"
        assert body["active_countries"] == 2


class TestRecentAndDistribution:
    def test_recent_returns_last_n_by_id_desc(self, client: TestClient) -> None:
        for name in ("A", "B", "C"):
            _post(client, full_name=name)

        body = client.get("/insights/recent", params={"limit": 2}).json()
        assert [row["full_name"] for row in body] == ["C", "B"]

    def test_distribution_returns_counts_per_country(self, client: TestClient) -> None:
        _post(client, country="IN")
        _post(client, country="IN")
        _post(client, country="US")

        body = client.get("/insights/distribution").json()
        assert body == {"counts": {"IN": 2, "US": 1}}
