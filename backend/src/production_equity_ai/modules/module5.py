"""Module 5: API orchestration endpoints."""
from fastapi import APIRouter
from sqlalchemy import func, select

from db.models import Company, DataQualityIssue, FinancialStatement, IngestionRun, Price, TreasuryRate
from db.session import session_scope

router = APIRouter()


@router.get("/summary", summary="API surface and dataset catalog")
def summary() -> dict:
    """Expose a compact catalog of stored resources and module capabilities."""

    with session_scope() as session:
        tickers = [row[0] for row in session.execute(select(Company.ticker)).all()]
        counts = {
            "companies": session.execute(select(func.count(Company.id))).scalar_one(),
            "financial_statements": session.execute(select(func.count(FinancialStatement.id))).scalar_one(),
            "prices": session.execute(select(func.count(Price.id))).scalar_one(),
            "treasury_rates": session.execute(select(func.count(TreasuryRate.id))).scalar_one(),
            "data_quality_issues": session.execute(select(func.count(DataQualityIssue.id))).scalar_one(),
            "ingestion_runs": session.execute(select(func.count(IngestionRun.id))).scalar_one(),
        }

    routes = {
        "module1": ["GET /module1/status", "POST /module1/ingest"],
        "module2": ["POST /module2/valuation"],
        "module3": ["GET /module3/signals"],
        "module4": ["GET /module4/backtest"],
        "module6": ["GET /module6/landing"],
        "module7": ["GET /module7/observability"],
    }

    return {
        "module": 5,
        "name": "API layer",
        "status": "ready" if counts["companies"] else "needs_ingestion",
        "tickers": tickers,
        "counts": counts,
        "routes": routes,
        "description": "Coordinates ingress, valuation, analytics, and monitoring endpoints exposed by Modules 1-7.",
    }
