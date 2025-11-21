"""Module 1: Data ingestion & preprocessing endpoints."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from db.models import Company, DataQualityIssue, FinancialStatement, IngestionRun, Price, TreasuryRate
from db.session import session_scope
from ingestion.pipeline import IngestionPipeline
from ingestion.storage import init_db

router = APIRouter()


class IngestionRequest(BaseModel):
    """Payload describing an ingestion run."""

    tickers: List[str] = Field(..., min_items=1, description="List of tickers to ingest")
    start: str = Field(..., description="Start date (YYYY-MM-DD)")
    end: str = Field(..., description="End date (YYYY-MM-DD)")
    treasury_rate_code: str = Field(
        "DGS10", description="FRED code for the treasury rate used in discounting"
    )


def _latest_run(session) -> Optional[IngestionRun]:
    return (
        session.execute(select(IngestionRun).order_by(IngestionRun.started_at.desc()))
        .scalars()
        .first()
    )


@router.get("/status", summary="Ingestion readiness and dataset footprint")
def status() -> dict:
    """Report ingestion health by counting persisted resources."""

    init_db()
    with session_scope() as session:
        counts = {
            "tickers": session.execute(select(func.count(Company.id))).scalar_one(),
            "statements": session.execute(select(func.count(FinancialStatement.id))).scalar_one(),
            "prices": session.execute(select(func.count(Price.id))).scalar_one(),
            "treasury_rates": session.execute(select(func.count(TreasuryRate.id))).scalar_one(),
            "quality_issues": session.execute(select(func.count(DataQualityIssue.id))).scalar_one(),
            "runs": session.execute(select(func.count(IngestionRun.id))).scalar_one(),
        }
        last_run = _latest_run(session)
        last_run_info = (
            None
            if not last_run
            else {
                "ticker": last_run.ticker,
                "status": last_run.status,
                "started_at": last_run.started_at,
                "message": last_run.message,
            }
        )

    return {
        "module": 1,
        "name": "Data ingestion & preprocessing",
        "status": "ready" if counts["treasury_rates"] else "needs_seed_data",
        "counts": counts,
        "last_run": last_run_info,
        "description": "Downloads statements, price history, and treasury curves with validation and persistence.",
    }


@router.post("/ingest", summary="Launch an ingestion run")
def ingest(request: IngestionRequest) -> dict:
    """Execute the ingestion pipeline synchronously for the requested tickers."""

    try:
        datetime.strptime(request.start, "%Y-%m-%d")
        datetime.strptime(request.end, "%Y-%m-%d")
    except ValueError as exc:  # noqa: B904
        raise HTTPException(status_code=400, detail="start and end must be YYYY-MM-DD") from exc

    init_db()
    pipeline = IngestionPipeline(
        tickers=request.tickers,
        start=request.start,
        end=request.end,
        treasury_rate_code=request.treasury_rate_code,
    )
    pipeline.run()

    with session_scope() as session:
        last_run = _latest_run(session)

    return {
        "message": "Ingestion completed",
        "tickers": request.tickers,
        "start": request.start,
        "end": request.end,
        "treasury_rate_code": request.treasury_rate_code,
        "last_run": {
            "ticker": last_run.ticker if last_run else None,
            "status": last_run.status if last_run else None,
            "started_at": last_run.started_at if last_run else None,
            "message": last_run.message if last_run else None,
        },
    }
