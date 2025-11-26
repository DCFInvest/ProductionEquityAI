"""Module 4: Portfolio simulation and backtesting endpoints."""
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from db.models import Company, Price
from db.session import session_scope

router = APIRouter()


def _load_prices(ticker: str) -> pd.DataFrame:
    with session_scope() as session:
        company = (
            session.execute(select(Company).where(Company.ticker == ticker.upper()))
            .scalars()
            .first()
        )
        if not company:
            raise HTTPException(status_code=404, detail="Ticker not found in the database")

        prices = (
            session.execute(
                select(Price).where(Price.company_id == company.id).order_by(Price.date)
            )
            .scalars()
            .all()
        )
    if not prices:
        raise HTTPException(status_code=400, detail="No price history available for backtesting")

    df = pd.DataFrame(
        {"date": [p.date for p in prices], "close": [p.close for p in prices]}
    ).set_index("date")
    df["return"] = df["close"].pct_change().fillna(0)
    return df


@router.get("/backtest", summary="Run SMA crossover backtest")
def backtest(
    ticker: str = Query(..., description="Ticker symbol"),
    fast_window: int = Query(20, ge=1, description="Short moving average window"),
    slow_window: int = Query(50, ge=1, description="Long moving average window"),
    initial_capital: float = 10_000,
) -> dict:
    """Simulate a moving-average crossover strategy against stored price history."""

    if fast_window >= slow_window:
        raise HTTPException(status_code=400, detail="fast_window must be less than slow_window")

    df = _load_prices(ticker)
    df["fast_ma"] = df["close"].rolling(window=fast_window).mean()
    df["slow_ma"] = df["close"].rolling(window=slow_window).mean()
    df.dropna(inplace=True)
    if df.empty:
        raise HTTPException(status_code=400, detail="Insufficient history for moving averages")

    df["signal"] = (df["fast_ma"] > df["slow_ma"]).astype(int)
    df["position"] = df["signal"].shift(1).fillna(0)
    df["strategy_return"] = df["position"] * df["return"]

    cumulative_return = (1 + df["strategy_return"]).prod() - 1
    buy_and_hold = (df["close"].iloc[-1] / df["close"].iloc[0]) - 1
    equity_curve = list(
        zip(
            df.index.strftime("%Y-%m-%d").tolist(),
            (initial_capital * (1 + df["strategy_return"]).cumprod()).round(2).tolist(),
        )
    )

    return {
        "module": 4,
        "name": "Backtesting & simulation",
        "ticker": ticker.upper(),
        "windows": {"fast": fast_window, "slow": slow_window},
        "performance": {
            "strategy_return": cumulative_return,
            "buy_and_hold_return": buy_and_hold,
            "trade_days": len(df),
        },
        "equity_curve": equity_curve[-10:],
    }
