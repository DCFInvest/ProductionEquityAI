"""Data source clients for ingestion."""
import logging
from datetime import datetime
from typing import List

import yfinance as yf
from pandas_datareader import data as pdr

from ingestion.validation import (
    FinancialStatementRecord,
    PriceRecord,
    TreasuryRateRecord,
)
from production_equity_ai.logging_config import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


def fetch_financial_statements(ticker: str) -> List[FinancialStatementRecord]:
    """Download and normalize financial statements for a ticker using yfinance."""

    logger.info("Fetching financial statements for %s", ticker)
    ticker_obj = yf.Ticker(ticker)
    statements = []
    statement_map = {
        "income_statement": ticker_obj.financials,
        "balance_sheet": ticker_obj.balance_sheet,
        "cash_flow": ticker_obj.cashflow,
    }
    for name, df in statement_map.items():
        if df is None or df.empty:
            logger.warning("No %s data for %s", name, ticker)
            continue
        df = df.fillna(0).astype(float)
        for fiscal_date, series in df.items():
            record = FinancialStatementRecord(
                ticker=ticker,
                fiscal_date=datetime.strptime(str(fiscal_date.date()), "%Y-%m-%d").date(),
                statement_type=name,
                data=series.to_dict(),
            )
            statements.append(record)
    return statements


def fetch_price_history(ticker: str, start: str, end: str, threads: int = 4) -> List[PriceRecord]:
    """Download historical prices for a ticker."""

    logger.info("Fetching price history for %s", ticker)
    df = yf.download(ticker, start=start, end=end, threads=threads, progress=False)
    if df.empty:
        logger.warning("No price data returned for %s", ticker)
        return []
    df = df.dropna()
    prices: List[PriceRecord] = []
    for index, row in df.iterrows():
        prices.append(
            PriceRecord(
                ticker=ticker,
                date=index.date(),
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                adjusted_close=float(row["Adj Close"]),
                volume=int(row["Volume"]),
            )
        )
    return prices


def fetch_treasury_rates(rate_code: str, start: str, end: str) -> List[TreasuryRateRecord]:
    """Download treasury rates from FRED using pandas_datareader."""

    logger.info("Fetching treasury rates %s", rate_code)
    df = pdr.DataReader(rate_code, "fred", start=start, end=end)
    df = df.dropna()
    rates: List[TreasuryRateRecord] = []
    for index, value in df.iterrows():
        rates.append(
            TreasuryRateRecord(
                date=index.date(),
                rate_type=rate_code,
                rate=float(value[rate_code]),
            )
        )
    return rates
