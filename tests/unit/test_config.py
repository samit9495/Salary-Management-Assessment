from app.core.config import Settings


def test_settings_reads_database_url_from_env(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./custom.db")
    settings = Settings()
    assert settings.database_url == "sqlite:///./custom.db"


def test_settings_defaults_database_url_to_local_sqlite(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = Settings()
    assert settings.database_url == "sqlite:///./salary.db"


def test_settings_parses_comma_separated_allowed_origins(monkeypatch) -> None:
    monkeypatch.setenv(
        "ALLOWED_ORIGINS", "https://a.example.com, https://b.example.com"
    )
    settings = Settings()
    assert settings.allowed_origins == [
        "https://a.example.com",
        "https://b.example.com",
    ]


def test_settings_parses_json_array_allowed_origins(monkeypatch) -> None:
    """Locks the BeforeValidator passthrough that defers JSON parsing.

    When ``ALLOWED_ORIGINS`` is a JSON array string (leading ``[``),
    ``_parse_origins`` must return the value unchanged so
    ``pydantic-settings`` can JSON-decode it. Without this branch the
    list would be one-elemented with the raw JSON string inside.
    """
    monkeypatch.setenv(
        "ALLOWED_ORIGINS",
        '["https://a.example.com", "https://b.example.com"]',
    )
    settings = Settings()
    assert settings.allowed_origins == [
        "https://a.example.com",
        "https://b.example.com",
    ]


def test_settings_defaults_log_level_to_info(monkeypatch) -> None:
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    settings = Settings()
    assert settings.log_level == "INFO"


def test_settings_reads_log_level_from_env(monkeypatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    settings = Settings()
    assert settings.log_level == "DEBUG"


def test_settings_defaults_log_sql_to_false(monkeypatch) -> None:
    monkeypatch.delenv("LOG_SQL", raising=False)
    settings = Settings()
    assert settings.log_sql is False


def test_settings_reads_log_sql_from_env(monkeypatch) -> None:
    monkeypatch.setenv("LOG_SQL", "true")
    settings = Settings()
    assert settings.log_sql is True
