"""Local quickstart ingestion script for demonstration."""
from datetime import datetime, timedelta

from ingestion.pipeline import IngestionPipeline


def main() -> None:
    """Run ingestion for a small demo set."""

    pipeline = IngestionPipeline(
        tickers=["AAPL", "MSFT"],
        start=(datetime.utcnow() - timedelta(days=365)).strftime("%Y-%m-%d"),
        end=datetime.utcnow().strftime("%Y-%m-%d"),
    )
    pipeline.run()


if __name__ == "__main__":
    main()
