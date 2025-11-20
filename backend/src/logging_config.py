"""Logging configuration utilities."""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from config import get_settings


def configure_logging(log_file: Optional[str] = None) -> None:
    """Configure root logger with console and optional file handlers."""

    settings = get_settings()
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    handlers = [logging.StreamHandler()]

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(
            RotatingFileHandler(
                filename=log_file, maxBytes=10_000_000, backupCount=5
            )
        )

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=handlers,
        force=True,
    )


configure_logging()
