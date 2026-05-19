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

    def test_get_employee_returns_404_when_missing(self, client: TestClient) -> None:
        response = client.get("/employees/9999")

        assert response.status_code == 404
        assert response.json()["code"] == "employee_not_found"


class TestListEmployeesAPI:
    def test_list_employees_returns_empty_list_when_no_rows(self, client: TestClient) -> None:
        response = client.get("/employees")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_employees_returns_inserted_rows(self, client: TestClient) -> None:
        client.post("/employees", json=_valid_payload(full_name="A"))
        client.post("/employees", json=_valid_payload(full_name="B"))

        response = client.get("/employees")
        assert response.status_code == 200
        names = [row["full_name"] for row in response.json()]
        assert names == ["A", "B"]

    def test_list_employees_paginates_with_limit_and_offset(self, client: TestClient) -> None:
        for name in ["A", "B", "C", "D"]:
            client.post("/employees", json=_valid_payload(full_name=name))

        page = client.get("/employees", params={"limit": 2, "offset": 1}).json()

        assert [row["full_name"] for row in page] == ["B", "C"]

    def test_list_employees_rejects_limit_over_max(self, client: TestClient) -> None:
        response = client.get("/employees", params={"limit": 501})
        assert response.status_code == 422

    def test_list_employees_defaults_limit_to_50(self, client: TestClient) -> None:
        for i in range(55):
            client.post("/employees", json=_valid_payload(full_name=f"N{i:02d}"))

        page = client.get("/employees").json()
        assert len(page) == 50

    def test_list_employees_filters_by_country(self, client: TestClient) -> None:
        client.post("/employees", json=_valid_payload(full_name="Indian", country="IN"))
        client.post("/employees", json=_valid_payload(full_name="American", country="US"))

        rows = client.get("/employees", params={"country": "IN"}).json()

        assert [row["full_name"] for row in rows] == ["Indian"]

    def test_list_employees_filters_by_name_substring_case_insensitive(
        self, client: TestClient
    ) -> None:
        client.post("/employees", json=_valid_payload(full_name="Jane Doe"))
        client.post("/employees", json=_valid_payload(full_name="John Smith"))
        client.post("/employees", json=_valid_payload(full_name="Jasmine Lee"))

        rows = client.get("/employees", params={"q": "ja"}).json()

        names = {row["full_name"] for row in rows}
        assert names == {"Jane Doe", "Jasmine Lee"}

    def test_list_employees_sort_by_salary_desc(self, client: TestClient) -> None:
        client.post("/employees", json=_valid_payload(full_name="Low", salary="100.00"))
        client.post("/employees", json=_valid_payload(full_name="High", salary="999.00"))
        client.post("/employees", json=_valid_payload(full_name="Mid", salary="500.00"))

        rows = client.get("/employees", params={"sort": "-salary"}).json()

        assert [r["full_name"] for r in rows] == ["High", "Mid", "Low"]

    def test_list_employees_rejects_unknown_sort_key(self, client: TestClient) -> None:
        response = client.get("/employees", params={"sort": "ssn"})
        assert response.status_code == 422


class TestUpdateEmployeeAPI:
    def test_put_employee_updates_provided_fields(self, client: TestClient) -> None:
        created = client.post("/employees", json=_valid_payload()).json()

        response = client.put(
            f"/employees/{created['id']}",
            json={"job_title": "Senior Engineer", "salary": "75000.00"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["job_title"] == "Senior Engineer"
        assert body["salary"] == "75000.00"
        assert body["full_name"] == "Jane Doe"  # unchanged

    def test_put_missing_employee_returns_404(self, client: TestClient) -> None:
        response = client.put("/employees/9999", json={"job_title": "X"})
        assert response.status_code == 404


class TestDeleteEmployeeAPI:
    def test_delete_employee_returns_204_and_removes_row(self, client: TestClient) -> None:
        created = client.post("/employees", json=_valid_payload()).json()

        response = client.delete(f"/employees/{created['id']}")
        assert response.status_code == 204
        assert response.content == b""

        follow_up = client.get(f"/employees/{created['id']}")
        assert follow_up.status_code == 404

    def test_delete_missing_employee_returns_404(self, client: TestClient) -> None:
        response = client.delete("/employees/9999")
        assert response.status_code == 404


class TestDuplicateEmail:
    def test_post_with_duplicate_email_returns_409(self, client: TestClient) -> None:
        client.post("/employees", json=_valid_payload(email="jane@example.com"))

        response = client.post("/employees", json=_valid_payload(email="jane@example.com"))

        assert response.status_code == 409
        assert response.json()["code"] == "duplicate_email"


class TestOptionalProfileFields:
    def test_create_defaults_is_active_to_true(self, client: TestClient) -> None:
        body = client.post("/employees", json=_valid_payload()).json()
        assert body["is_active"] is True

    def test_create_persists_department_and_hire_date(self, client: TestClient) -> None:
        payload = _valid_payload(department="Platform", hire_date="2024-01-15")

        body = client.post("/employees", json=payload).json()

        assert body["department"] == "Platform"
        assert body["hire_date"] == "2024-01-15"
