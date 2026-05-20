import json
from typing import Annotated

from pydantic import BeforeValidator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


def _parse_origins(value: object) -> object:
    """Accept either a comma-separated string or a JSON array string.

    ``NoDecode`` suppresses pydantic-settings' built-in JSON decoding,
    so this validator owns both shapes.
    """
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith("["):
            return json.loads(stripped)
        return [item.strip() for item in stripped.split(",") if item.strip()]
    return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./salary.db"
    allowed_origins: Annotated[list[str], NoDecode, BeforeValidator(_parse_origins)] = [
        "http://localhost:5173"
    ]
    log_level: str = "INFO"
    log_sql: bool = False


def get_settings() -> Settings:
    return Settings()
