"""Storage utilities for persisting ingested data."""
import logging
from typing import List, Optional

from sqlalchemy import select

from db.base import Base
from db.models import (
    Company,
    DataQualityIssue,
    FinancialStatement,
    IngestionRun,
    Price,
    TreasuryRate,
)
from db.session import engine, session_scope
from ingestion.validation import FinancialStatementRecord, PriceRecord, TreasuryRateRecord

logger = logging.getLogger(__name__)


def init_db() -> None:
    """Create all tables if they do not exist."""

    Base.metadata.create_all(bind=engine)


def upsert_company(ticker: str, session) -> Company:
    """Fetch or create a company record by ticker within a session."""

    company = session.execute(select(Company).where(Company.ticker == ticker)).scalar_one_or_none()
    if company:
        return company
    company = Company(ticker=ticker)
    session.add(company)
    session.flush()
    return company


def store_financial_statements(statements: List[FinancialStatementRecord]) -> None:
    """Persist validated financial statements."""

    with session_scope() as session:
        for record in statements:
            company = upsert_company(record.ticker, session)
            session.merge(
                FinancialStatement(
                    company_id=company.id,
                    fiscal_date=record.fiscal_date,
                    statement_type=record.statement_type,
                    data=record.data,
                )
            )


def store_prices(prices: List[PriceRecord]) -> None:
    """Persist validated price history records."""

    with session_scope() as session:
        for record in prices:
            company = upsert_company(record.ticker, session)
            session.merge(
                Price(
                    company_id=company.id,
                    date=record.date,
                    open=record.open,
                    high=record.high,
                    low=record.low,
                    close=record.close,
                    adjusted_close=record.adjusted_close,
                    volume=record.volume,
                )
            )


def store_treasury_rates(rates: List[TreasuryRateRecord]) -> None:
    """Persist treasury rate history."""

    with session_scope() as session:
        for record in rates:
            session.merge(
                TreasuryRate(
                    date=record.date, rate_type=record.rate_type, rate=record.rate
                )
            )


def record_quality_issue(issue_type: str, description: str, context: Optional[dict] = None) -> None:
    """Create a data quality issue entry."""

    with session_scope() as session:
        session.add(
            DataQualityIssue(issue_type=issue_type, description=description, context=context)
        )


def start_run(ticker: Optional[str]) -> IngestionRun:
    """Create an ingestion run record."""

    with session_scope() as session:
        run = IngestionRun(ticker=ticker)
        session.add(run)
        session.flush()
        session.refresh(run)
        return run


def complete_run(run_id: int, status: str, message: Optional[str] = None) -> None:
    """Finalize an ingestion run with status and message."""

    with session_scope() as session:
        run = session.get(IngestionRun, run_id)
        if not run:
            logger.error("Attempted to complete missing run %s", run_id)
            return
        run.status = status
        run.message = message
        session.add(run)
