# ProductionEquityAI

ProductionEquityAI is a full-stack platform for AI-driven equity analysis. This repository now ships with **Modules 1-7** wired
into a single deployable service that can be uploaded directly to Render.

## Module Overview
- **Module 1: Data ingestion & preprocessing** – downloads historical **financial statements**, **stock prices**, and **treasury
  rates**, cleans the data, and validates it with strict dataclass validation before persistence.
- **Module 2: Valuation engine** – runs DCF, multiples, and comparables using normalized fundamentals and rates.
- **Module 3: ML modeling** – supports supervised learning on historical signals and forward inference.
- **Module 4: Backtesting & simulation** – runs scenario analysis, portfolio construction, and risk evaluation.
- **Module 5: API layer** – exposes consolidated endpoints across ingestion, valuation, ML, and analytics.
- **Module 6: Frontend delivery** – serves UI assets or proxies to the frontend experience for Render deployments.
- **Module 7: Observability & operations** – handles alerting, scheduled jobs, and deployment automation signals.

Each module is surfaced as a FastAPI router under `/module{N}` with real functionality:
- `/module1/ingest` runs the data ingestion pipeline and `/module1/status` reports stored counts and last run.
- `/module2/valuation` executes a lightweight discounted cash flow using ingested cash flow statements and treasury rates.
- `/module3/signals` derives engineered momentum/volatility signals for a ticker using persisted prices.
- `/module4/backtest` simulates a moving-average crossover strategy against stored prices.
- `/module5/summary` advertises available routes and dataset coverage.
- `/module6/landing` serves a minimal HTML page that links to all module endpoints and shows loaded tickers.
- `/module7/observability` lists recent ingestion runs and open data-quality alerts.

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

### Running the API locally

```
PYTHONPATH=backend/src uvicorn production_equity_ai.app:app --reload --host 0.0.0.0 --port 8000
```

- Health check: `http://localhost:8000/health`
- Module status endpoints: `http://localhost:8000/module1/status` … `http://localhost:8000/module7/status`

### Running Ingestion (Module 1)
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

### Deploying to Render
1. Ensure your Render account has access to a PostgreSQL instance (or configure `DATABASE_URL` for SQLite).
2. Push this repository to GitHub.
3. In Render, create a new **Web Service** and point it at the repo.
4. Confirm the following settings (also captured in `render.yaml`):
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `PYTHONPATH=backend/src uvicorn production_equity_ai.app:app --host 0.0.0.0 --port $PORT`
5. Add environment variables for `DATABASE_URL`, `LOG_LEVEL`, and any other secrets required by your modules.

Deployments will automatically expose the FastAPI documentation at `/docs` and `/redoc`, giving you a single surface to test
Modules 1-7.

## Repository Structure
- `backend/src/production_equity_ai` – unified FastAPI app, shared config, logging, and module routers.
- `backend/requirements.txt` – Python dependencies for all modules and deployment.
- `render.yaml` – Render Blueprint for one-click deployment.

## Module Outputs & Next Steps
- **Outputs**: Populated `companies`, `financial_statements`, `prices`, `treasury_rates`, and ingestion metadata tables with
  validated, cleaned data ready for downstream analytics.
- **Integration**: Module 1 feeds the valuation engine (Module 2) via the normalized database. Valuation models can query
  financials and rates directly. Module 3’s deep learning will use the same tables for supervised training.
- **Next**: Implement the detailed business logic inside each FastAPI module router, add API endpoints for retrieval, and
  extend tests around valuation, ML modeling, and portfolio simulations.
