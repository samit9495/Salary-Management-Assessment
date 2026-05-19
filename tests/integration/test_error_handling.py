from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import DomainError
from app.main import register_exception_handlers


def test_domainerror_is_mapped_to_500_with_code() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    def boom() -> None:
        raise DomainError("something failed")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/boom")

    assert response.status_code == 500
    body = response.json()
    assert body == {"detail": "something failed", "code": "domain_error"}
