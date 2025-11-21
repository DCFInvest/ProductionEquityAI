"""Module 7: Observability and operations endpoints."""
from fastapi import APIRouter
from sqlalchemy import select

from db.models import DataQualityIssue, IngestionRun
from db.session import session_scope

router = APIRouter()


@router.get("/observability", summary="Ingestion health and alerts")
def observability(limit: int = 10) -> dict:
    """Return recent ingestion runs and unresolved data quality issues."""

    with session_scope() as session:
        issues = (
            session.execute(
                select(DataQualityIssue)
                .order_by(DataQualityIssue.created_at.desc())
                .limit(limit)
            )
            .scalars()
            .all()
        )
        runs = (
            session.execute(
                select(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(limit)
            )
            .scalars()
            .all()
        )

    return {
        "module": 7,
        "name": "Observability & operations",
        "issues": [
            {
                "id": issue.id,
                "type": issue.issue_type,
                "description": issue.description,
                "resolved": bool(issue.resolved),
                "created_at": issue.created_at,
            }
            for issue in issues
        ],
        "recent_runs": [
            {
                "id": run.id,
                "ticker": run.ticker,
                "status": run.status,
                "started_at": run.started_at,
                "message": run.message,
            }
            for run in runs
        ],
        "unresolved_issue_count": len([issue for issue in issues if not issue.resolved]),
    }
