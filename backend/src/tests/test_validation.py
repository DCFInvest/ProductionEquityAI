"""Unit tests for validation schemas."""
from datetime import date

import pytest

from ingestion.validation import PriceRecord


def test_price_record_validates_high_above_low() -> None:
    """High cannot be less than low during validation."""

    with pytest.raises(ValueError):
        PriceRecord(
            ticker="TEST",
            date=date(2024, 1, 1),
            open=10,
            high=5,
            low=6,
            close=9,
            adjusted_close=9,
            volume=1000,
        )


def test_price_record_success() -> None:
    """Valid price record initializes without error."""

    record = PriceRecord(
        ticker="TEST",
        date=date(2024, 1, 1),
        open=10,
        high=12,
        low=9,
        close=11,
        adjusted_close=11,
        volume=1000,
    )
    assert record.high == 12
