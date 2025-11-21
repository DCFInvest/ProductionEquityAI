"""Ingestion pipeline orchestrating downloads, validation, and persistence."""
import logging
from datetime import datetime
from typing import Callable, List, Sequence

from production_equity_ai.config import get_settings
from ingestion import data_sources
from ingestion.validation import (
    FinancialStatementRecord,
    PriceRecord,
    TreasuryRateRecord,
    ValidationReport,
    validate_records,
)
from ingestion.storage import (
    complete_run,
    init_db,
    record_quality_issue,
    start_run,
    store_financial_statements,
    store_prices,
    store_treasury_rates,
)

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Pipeline to ingest financial statements, prices, and treasury rates."""

    def __init__(
        self,
        tickers: Sequence[str],
        start: str,
        end: str,
        treasury_rate_code: str = "DGS10",
        financial_fetcher: Callable[[str], List[FinancialStatementRecord]] = data_sources.fetch_financial_statements,
        price_fetcher: Callable[[str, str, str, int], List[PriceRecord]] = data_sources.fetch_price_history,
        rate_fetcher: Callable[[str, str, str], List[TreasuryRateRecord]] = data_sources.fetch_treasury_rates,
    ) -> None:
        self.tickers = tickers
        self.start = start
        self.end = end
        self.treasury_rate_code = treasury_rate_code
        self.financial_fetcher = financial_fetcher
        self.price_fetcher = price_fetcher
        self.rate_fetcher = rate_fetcher
        self.settings = get_settings()

    def run(self) -> None:
        """Execute the end-to-end ingestion pipeline."""

        init_db()
        self._ingest_treasury_rates()
        for ticker in self.tickers:
            run = start_run(ticker)
            try:
                self._ingest_ticker(ticker)
                complete_run(run.id, status="success")
            except Exception as exc:  # noqa: BLE001
                logger.exception("Ingestion failed for %s", ticker)
                complete_run(run.id, status="failed", message=str(exc))

    def _ingest_treasury_rates(self) -> None:
        """Ingest treasury rates prior to ticker-specific data."""

        rates = self.rate_fetcher(self.treasury_rate_code, self.start, self.end)
        report = validate_records(rates)
        if report.failed:
            record_quality_issue(
                "treasury_rate_validation",
                "Validation errors in treasury rates",
                {"errors": report.errors},
            )
        store_treasury_rates(rates)
        logger.info(
            "Stored %s treasury rates (%s failed validation)", report.passed, report.failed
        )

    def _ingest_ticker(self, ticker: str) -> None:
        """Ingest statements and prices for a single ticker."""

        statements = self.financial_fetcher(ticker)
        statement_report = validate_records(statements)
        if statement_report.failed:
            record_quality_issue(
                "statement_validation",
                f"Validation errors for {ticker}",
                {"errors": statement_report.errors},
            )
        store_financial_statements(statements)

        prices = self.price_fetcher(
            ticker, self.start, self.end, threads=self.settings.yfinance_threads
        )
        price_report = validate_records(prices)
        if price_report.failed:
            record_quality_issue(
                "price_validation", f"Validation errors for {ticker}", {"errors": price_report.errors}
            )
        store_prices(prices)

        logger.info(
            "Ingested %s statements and %s price points for %s",
            statement_report.passed,
            price_report.passed,
            ticker,
        )
