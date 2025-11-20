"""Validation schemas for ingested data."""
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List


@dataclass
class FinancialStatementRecord:
    """Validated financial statement entry."""

    ticker: str
    fiscal_date: date
    statement_type: str
    data: Dict[str, float]

    def __post_init__(self) -> None:
        if not (1 <= len(self.ticker) <= 10):
            raise ValueError("ticker length must be between 1 and 10 characters")
        if not (2 <= len(self.statement_type) <= 50):
            raise ValueError("statement_type length must be between 2 and 50 characters")
        cleaned = {}
        for key, val in self.data.items():
            cleaned[key] = float(val)
        self.data = cleaned


@dataclass
class PriceRecord:
    """Validated stock price record."""

    ticker: str
    date: date
    open: float
    high: float
    low: float
    close: float
    adjusted_close: float
    volume: int

    def __post_init__(self) -> None:
        if not (1 <= len(self.ticker) <= 10):
            raise ValueError("ticker length must be between 1 and 10 characters")
        if self.high < self.low:
            raise ValueError("high cannot be lower than low")
        if any(value is None for value in [self.open, self.high, self.low, self.close]):
            raise ValueError("price fields cannot be None")


@dataclass
class TreasuryRateRecord:
    """Validated treasury rate record."""

    date: date
    rate_type: str
    rate: float

    def __post_init__(self) -> None:
        if not self.rate_type:
            raise ValueError("rate_type is required")


@dataclass
class ValidationReport:
    """Summarize validation outcomes for a batch."""

    total: int
    passed: int
    failed: int
    errors: List[str] = field(default_factory=list)


def validate_records(records: List[object]) -> ValidationReport:
    """Validate dataclass records by invoking their validation logic."""

    total = len(records)
    errors: List[str] = []
    passed = 0
    for record in records:
        try:
            if hasattr(record, "__post_init__"):
                record.__post_init__()
            passed += 1
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))
    failed = total - passed
    return ValidationReport(total=total, passed=passed, failed=failed, errors=errors)
