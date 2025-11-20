"""Example script to run full ingestion pipeline."""
import argparse
import logging
from datetime import datetime, timedelta

from config import get_settings
from ingestion.pipeline import IngestionPipeline

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for ingestion."""

    parser = argparse.ArgumentParser(description="Ingest financial data for tickers")
    parser.add_argument("tickers", nargs="+", help="List of ticker symbols")
    parser.add_argument(
        "--start", default=(datetime.utcnow() - timedelta(days=365 * 5)).strftime("%Y-%m-%d")
    )
    parser.add_argument("--end", default=datetime.utcnow().strftime("%Y-%m-%d"))
    parser.add_argument(
        "--treasury-rate", default="DGS10", help="FRED code for treasury rate"
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for running ingestion from the command line."""

    args = parse_args()
    settings = get_settings()
    logger.info("Using database %s", settings.database_url)
    pipeline = IngestionPipeline(
        tickers=args.tickers,
        start=args.start,
        end=args.end,
        treasury_rate_code=args.treasury_rate,
    )
    pipeline.run()


if __name__ == "__main__":
    main()
