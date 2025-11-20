"""Application configuration and environment variable management."""
import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class Settings:
    """Centralized application settings loaded from environment variables."""

    database_url: str
    log_level: str
    yfinance_threads: int


def _get_env(key: str, default: str) -> str:
    """Return an environment variable with fallback."""

    return os.getenv(key, default)


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings populated from environment."""

    return Settings(
        database_url=_get_env("DATABASE_URL", "sqlite:///./data.db"),
        log_level=_get_env("LOG_LEVEL", "INFO"),
        yfinance_threads=int(_get_env("YFINANCE_THREADS", "4")),
    )
