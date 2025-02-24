from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_TITLE: str = "Waste Recognition API"
    APP_DESCRIPTION: str = "API for waste recognition apps"
    APP_VERSION: str = "0.1.0"

    DEBUG: bool = False

    CSRF_COOKIE_NAME: str = "csrftoken"  # noqa: Typo
    CSRF_EXPIRE_TIME: int = 86400 * 7  # 7 дней  # noqa: Typo

    DOMAIN: str = "example.site"

    ALLOW_ORIGINS: list[str] = ["*"]
    ALLOW_HOSTS: list[str] = ["*"]

    API_PREFIX: str = "/api"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parents[1] / ".env", extra="ignore"
    )


@lru_cache
def get_settings():
    return Settings()