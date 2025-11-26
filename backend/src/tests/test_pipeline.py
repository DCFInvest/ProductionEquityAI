"""Integration tests for ingestion pipeline using in-memory database."""
import os
from datetime import date
from importlib import reload
from typing import List

import pytest

from production_equity_ai import config
from db import session as session_module
from ingestion import pipeline as pipeline_module
from ingestion import storage as storage_module
from db.models import Company, FinancialStatement, Price, TreasuryRate
from ingestion.validation import FinancialStatementRecord, PriceRecord, TreasuryRateRecord


@pytest.fixture(autouse=True)
def configure_sqlite(tmp_path) -> None:
    """Configure an isolated SQLite database for each test."""

    os.environ["DATABASE_URL"] = f"sqlite:///{tmp_path}/test.db"
    config.get_settings.cache_clear()
    reload(config)
    reload(session_module)
    reload(storage_module)
    reload(pipeline_module)
    yield
    config.get_settings.cache_clear()


def fake_financial_fetcher(ticker: str) -> List[FinancialStatementRecord]:
    """Return a deterministic financial statement payload."""

    return [
        FinancialStatementRecord(
            ticker=ticker,
            fiscal_date=date(2023, 12, 31),
            statement_type="income_statement",
            data={"revenue": 1000.0, "net_income": 100.0},
        )
    ]


def fake_price_fetcher(ticker: str, start: str, end: str, threads: int) -> List[PriceRecord]:
    """Return two days of synthetic prices."""

    return [
        PriceRecord(
            ticker=ticker,
            date=date(2024, 1, 1),
            open=10,
            high=12,
            low=9,
            close=11,
            adjusted_close=11,
            volume=100,
        ),
        PriceRecord(
            ticker=ticker,
            date=date(2024, 1, 2),
            open=11,
            high=13,
            low=10,
            close=12,
            adjusted_close=12,
            volume=200,
        ),
    ]


def fake_treasury_fetcher(rate_code: str, start: str, end: str) -> List[TreasuryRateRecord]:
    """Return a simple treasury rate series."""

    return [
        TreasuryRateRecord(date=date(2024, 1, 1), rate_type=rate_code, rate=4.5),
        TreasuryRateRecord(date=date(2024, 1, 2), rate_type=rate_code, rate=4.6),
    ]


def test_pipeline_persists_data() -> None:
    """Pipeline stores statements, prices, and rates using fake fetchers."""

    pipeline = pipeline_module.IngestionPipeline(
        tickers=["FAKE"],
        start="2024-01-01",
        end="2024-02-01",
        financial_fetcher=fake_financial_fetcher,
        price_fetcher=fake_price_fetcher,
        rate_fetcher=fake_treasury_fetcher,
    )
    pipeline.run()

    # Verify counts directly against the database
    with session_module.session_scope() as session:
        company_count = session.query(Company).count()
        statement_count = session.query(FinancialStatement).count()
        price_count = session.query(Price).count()
        rate_count = session.query(TreasuryRate).count()
    assert company_count == 1
    assert statement_count == 1
    assert price_count == 2
    assert rate_count == 2
