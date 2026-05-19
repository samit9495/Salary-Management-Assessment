import logging
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Column, Integer, Table, create_engine, inspect

from app.db.base import Base
from app.db.session import init_db
from app.main import app


def test_init_db_creates_registered_tables() -> None:
    Table(
        "_init_db_smoke",
        Base.metadata,
        Column("id", Integer, primary_key=True),
        extend_existing=True,
    )
    eng = create_engine("sqlite:///:memory:", future=True)
    try:
        init_db(eng)
        assert "_init_db_smoke" in set(inspect(eng).get_table_names())
    finally:
        Base.metadata.remove(Base.metadata.tables["_init_db_smoke"])
        eng.dispose()


@pytest.fixture
def _reset_root_logger() -> Iterator[None]:
    yield
    root = logging.getLogger()
    for handler in list(root.handlers):
        if getattr(handler, "_salary_management_handler", False):
            root.removeHandler(handler)
    root.setLevel(logging.WARNING)


def test_lifespan_installs_json_handler_on_root_logger(
    _reset_root_logger: None,
) -> None:
    with TestClient(app):
        marked = [
            h
            for h in logging.getLogger().handlers
            if getattr(h, "_salary_management_handler", False)
        ]

    assert len(marked) == 1


def test_lifespan_sets_root_log_level_from_settings(
    monkeypatch: pytest.MonkeyPatch,
    _reset_root_logger: None,
) -> None:
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    with TestClient(app):
        assert logging.getLogger().level == logging.DEBUG
