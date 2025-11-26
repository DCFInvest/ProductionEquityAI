"""Module 2: Valuation engine endpoints."""
from statistics import mean
from typing import List, Optional, Tuple

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from db.models import Company, FinancialStatement, Price, TreasuryRate
from db.session import session_scope

router = APIRouter()


class ValuationRequest(BaseModel):
    """DCF valuation inputs."""

    ticker: str = Field(..., description="Ticker symbol")
    growth_rate: float = Field(0.03, description="Annual FCF growth rate assumption")
    terminal_growth: float = Field(0.02, description="Perpetual growth beyond forecast horizon")
    equity_risk_premium: float = Field(0.05, description="Equity risk premium to add to risk-free rate")
    years: int = Field(5, ge=1, le=10, description="Projection years")


def _get_company(session, ticker: str) -> Optional[Company]:
    return (
        session.execute(select(Company).where(Company.ticker == ticker.upper()))
        .scalars()
        .first()
    )


def _latest_close(session, company: Company) -> Optional[float]:
    price = (
        session.execute(
            select(Price).where(Price.company_id == company.id).order_by(Price.date.desc())
        )
        .scalars()
        .first()
    )
    return price.close if price else None


def _risk_free_rate(session) -> float:
    latest_rate = (
        session.execute(select(TreasuryRate).order_by(TreasuryRate.date.desc()))
        .scalars()
        .first()
    )
    if latest_rate:
        return latest_rate.rate / 100
    return 0.04


def _free_cash_flows(session, company: Company) -> List[Tuple[str, float]]:
    records = (
        session.execute(
            select(FinancialStatement)
            .where(
                FinancialStatement.company_id == company.id,
                FinancialStatement.statement_type == "cash_flow",
            )
            .order_by(FinancialStatement.fiscal_date.desc())
        )
        .scalars()
        .all()
    )
    flows: List[Tuple[str, float]] = []
    keys = ["Free Cash Flow", "FreeCashFlow", "FreeCashFlow", "free_cash_flow"]
    for record in records:
        data = record.data or {}
        value: Optional[float] = None
        for key in keys:
            if key in data and data[key] is not None:
                try:
                    value = float(data[key])
                    break
                except (TypeError, ValueError):
                    continue
        if value is not None:
            flows.append((str(record.fiscal_date), value))
    return flows


@router.post("/valuation", summary="Run a lightweight DCF")
def valuation(payload: ValuationRequest) -> dict:
    """Calculate a simplified discounted cash flow valuation for a ticker."""

    with session_scope() as session:
        company = _get_company(session, payload.ticker)
        if not company:
            raise HTTPException(status_code=404, detail="Ticker not found in the database")

        cash_flows = _free_cash_flows(session, company)
        if not cash_flows:
            raise HTTPException(status_code=400, detail="No cash flow data available for valuation")

        discount_rate = _risk_free_rate(session) + payload.equity_risk_premium
        if discount_rate <= payload.terminal_growth:
            raise HTTPException(
                status_code=400,
                detail="Discount rate must exceed terminal growth to compute terminal value",
            )

        average_fcf = mean([value for _, value in cash_flows])
        projections = []
        for year in range(1, payload.years + 1):
            projected = average_fcf * (1 + payload.growth_rate) ** year
            discounted = projected / ((1 + discount_rate) ** year)
            projections.append({"year": year, "projected_fcf": projected, "discounted_fcf": discounted})

        terminal_cash_flow = projections[-1]["projected_fcf"] * (1 + payload.terminal_growth)
        terminal_value = terminal_cash_flow / (discount_rate - payload.terminal_growth)
        discounted_terminal = terminal_value / ((1 + discount_rate) ** payload.years)

        implied_equity_value = sum(p["discounted_fcf"] for p in projections) + discounted_terminal
        last_close = _latest_close(session, company)

    return {
        "module": 2,
        "name": "Valuation engine",
        "method": "discounted_cash_flow",
        "ticker": company.ticker,
        "assumptions": {
            "growth_rate": payload.growth_rate,
            "terminal_growth": payload.terminal_growth,
            "equity_risk_premium": payload.equity_risk_premium,
            "risk_free_rate": round(discount_rate - payload.equity_risk_premium, 4),
            "discount_rate": round(discount_rate, 4),
            "years": payload.years,
        },
        "cash_flows": cash_flows,
        "projections": projections,
        "terminal_value": terminal_value,
        "equity_value": implied_equity_value,
        "market_snapshot": {"last_close": last_close},
    }
