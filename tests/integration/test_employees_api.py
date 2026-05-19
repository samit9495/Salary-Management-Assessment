from fastapi import status
from fastapi.testclient import TestClient


def _valid_payload(**overrides: object) -> dict[str, object]:
    base = {
        "full_name": "Jane Doe",
        "job_title": "Engineer",
        "country": "IN",
        "salary": "50000.00",
    }
    base.update(overrides)
    return base


class TestCreateEmployeeAPI:
    def test_post_employees_returns_201_with_persisted_row(self, client: TestClient) -> None:
        response = client.post("/employees", json=_valid_payload())

        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body["id"] > 0
        assert body["full_name"] == "Jane Doe"
        assert body["country"] == "IN"
        assert body["salary"] == "50000.00"

    def test_post_employees_with_negative_salary_returns_422(self, client: TestClient) -> None:
        response = client.post("/employees", json=_valid_payload(salary="-1.00"))
        assert response.status_code == 422

    def test_post_employees_with_3_letter_country_returns_422(self, client: TestClient) -> None:
        response = client.post("/employees", json=_valid_payload(country="IND"))
        assert response.status_code == 422

    def test_post_employees_with_blank_full_name_returns_422(self, client: TestClient) -> None:
        response = client.post("/employees", json=_valid_payload(full_name=""))
        assert response.status_code == 422


class TestGetEmployeeAPI:
    def test_get_employee_by_id_returns_200_with_row(self, client: TestClient) -> None:
        created = client.post("/employees", json=_valid_payload()).json()

        response = client.get(f"/employees/{created['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]
