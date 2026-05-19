from app.core.config import Settings


def test_settings_reads_database_url_from_env(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./custom.db")
    settings = Settings()
    assert settings.database_url == "sqlite:///./custom.db"


def test_settings_defaults_database_url_to_local_sqlite(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = Settings()
    assert settings.database_url == "sqlite:///./salary.db"
