import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.middleware.request_context import (
    REQUEST_ID_HEADER,
    RequestContextMiddleware,
)
from app.core.logging import request_id_var

MIDDLEWARE_LOGGER = "app.api.middleware.request_context"


@pytest.fixture
def fixture_app() -> FastAPI:
    test_app = FastAPI()
    test_app.add_middleware(RequestContextMiddleware)

    @test_app.get("/echo-id")
    def echo_id() -> dict[str, str | None]:
        return {"request_id": request_id_var.get()}

    @test_app.get("/")
    def root() -> dict[str, str]:
        return {"status": "ok"}

    return test_app


def test_generates_request_id_when_inbound_header_absent(
    fixture_app: FastAPI,
) -> None:
    response = TestClient(fixture_app).get("/echo-id")

    assert response.status_code == 200
    request_id = response.headers.get(REQUEST_ID_HEADER)
    assert request_id
    assert response.json()["request_id"] == request_id


def test_echoes_inbound_request_id_header(fixture_app: FastAPI) -> None:
    response = TestClient(fixture_app).get(
        "/echo-id", headers={REQUEST_ID_HEADER: "trace-123"}
    )

    assert response.headers[REQUEST_ID_HEADER] == "trace-123"
    assert response.json()["request_id"] == "trace-123"


def test_emits_one_info_access_log_per_request(
    fixture_app: FastAPI,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.DEBUG)

    response = TestClient(fixture_app).get("/echo-id")

    records = [r for r in caplog.records if r.name == MIDDLEWARE_LOGGER]
    assert len(records) == 1
    record = records[0]
    assert record.levelno == logging.INFO
    assert record.method == "GET"
    assert record.path == "/echo-id"
    assert record.status_code == 200
    assert isinstance(record.duration_ms, float)
    assert record.duration_ms >= 0
    assert record.request_id == response.headers[REQUEST_ID_HEADER]


def test_health_check_logs_at_debug_not_info(
    fixture_app: FastAPI,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.DEBUG)

    TestClient(fixture_app).get("/")

    middleware_records = [r for r in caplog.records if r.name == MIDDLEWARE_LOGGER]
    assert len(middleware_records) == 1
    assert middleware_records[0].levelno == logging.DEBUG
    assert middleware_records[0].path == "/"
