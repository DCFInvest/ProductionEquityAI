"""Module 3: ML modeling endpoints."""
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from db.models import Company, Price
from db.session import session_scope

router = APIRouter()


def _price_frame(ticker: str) -> pd.DataFrame:
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
        raise HTTPException(status_code=400, detail="No price history available for modeling")

    df = pd.DataFrame(
        {"date": [p.date for p in prices], "close": [p.close for p in prices]}
    ).set_index("date")
    df["return"] = df["close"].pct_change()
    df.dropna(inplace=True)
    return df


def _latest_features(df: pd.DataFrame, window: int) -> dict:
    if window <= 0:
        raise HTTPException(status_code=400, detail="window must be a positive integer")

    recent = df.tail(window)
    if len(recent) < window:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough data to compute signals (requires {window} days)",
        )

    momentum = (recent["close"].iloc[-1] / recent["close"].iloc[0]) - 1
    volatility = recent["return"].std() * np.sqrt(252)
    recent["sma_fast"] = recent["close"].rolling(window=5).mean()
    recent["sma_slow"] = recent["close"].rolling(window=10).mean()
    crossover = "bullish" if recent["sma_fast"].iloc[-1] > recent["sma_slow"].iloc[-1] else "bearish"

    x = np.arange(len(recent))
    slope, _ = np.polyfit(x, recent["close"], 1)
    trend = "uptrend" if slope > 0 else "downtrend"

    return {
        "momentum": momentum,
        "volatility": volatility,
        "sma_fast": recent["sma_fast"].iloc[-1],
        "sma_slow": recent["sma_slow"].iloc[-1],
        "crossover": crossover,
        "trend": trend,
        "slope": slope,
    }


@router.get("/signals", summary="Derive momentum-based ML signals")
def signals(
    ticker: str = Query(..., description="Ticker symbol"),
    window: int = Query(30, ge=1, description="Lookback window for features"),
) -> dict:
    """Generate engineered features and a heuristic label for a ticker."""

    df = _price_frame(ticker)
    features = _latest_features(df, window)
    label = "buy" if features["crossover"] == "bullish" and features["trend"] == "uptrend" else "hold"

    return {
        "module": 3,
        "name": "ML modeling",
        "ticker": ticker.upper(),
        "window": window,
        "features": features,
        "label": label,
    }
