# ProductionEquityAI

ProductionEquityAI is a full-stack platform for AI-driven equity analysis. This iteration delivers **Module 1: Data ingestion & preprocessing**, establishing reliable pipelines for fundamentals, prices, and treasury rates.

## Module 1 Overview
- Downloads historical **financial statements**, **stock prices**, and **treasury rates**.
- Cleans and validates data with strict dataclass validation before persistence.
- Stores information in a PostgreSQL-ready database via SQLAlchemy (SQLite defaults for local runs).
- Provides run metadata, data quality issue tracking, and structured logging.
- Ships with unit/integration tests and example scripts.

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL (for production) or SQLite (default dev)
- Recommended: create a virtual environment

### Environment
Set environment variables (or a `.env` file) to configure the service:

```
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/production_equity
LOG_LEVEL=INFO
YFINANCE_THREADS=4
```

If no variables are provided, the system falls back to `sqlite:///./data.db`.

### Installation

```
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If outbound package downloads are blocked (e.g., corporate proxy restrictions), install the requirements from an approved
internal mirror or pre-downloaded wheels before running tests.

### Running Ingestion
- Full control via CLI:
  ```
  PYTHONPATH=./src python -m scripts.ingest_all AAPL MSFT --start 2020-01-01 --end 2024-01-01 --treasury-rate DGS10
  ```
- Quick demo (defaults to last 12 months of AAPL/MSFT):
  ```
  PYTHONPATH=./src python -m scripts.ingest_sample
  ```

### Tests

```
cd backend
pytest
```

### Module Outputs & Next Steps
- **Outputs**: Populated `companies`, `financial_statements`, `prices`, `treasury_rates`, and ingestion metadata tables with validated, cleaned data ready for downstream analytics.
- **Integration**: Module 1 feeds the valuation engine (Module 2) via the normalized database. Valuation models can query financials and rates directly. Module 3’s deep learning will use the same tables for supervised training.
- **Next**: Build the valuation engine (DCF, multiples, comparables) consuming these tables, add API endpoints for retrieval, and extend tests around valuation logic.
