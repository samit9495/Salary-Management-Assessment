from fastapi.testclient import TestClient

from app.main import app


def test_cors_allows_frontend_origin_preflight() -> None:
    client = TestClient(app)
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code in (200, 204)
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_rejects_unknown_origin() -> None:
    client = TestClient(app)
    response = client.options(
        "/",
        headers={
            "Origin": "http://evil.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in response.headers
