"""Module 6: Frontend delivery and assets endpoints."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from sqlalchemy import select

from db.models import Company
from db.session import session_scope

router = APIRouter()


@router.get("/landing", response_class=HTMLResponse, summary="Simple HTML landing page")
def landing() -> str:
    """Serve a minimal HTML page highlighting available modules and tickers."""

    with session_scope() as session:
        tickers = [row[0] for row in session.execute(select(Company.ticker)).all()]

    ticker_list = "".join(f"<li>{ticker}</li>" for ticker in tickers) or "<li>None ingested yet</li>"
    html = f"""
    <html>
      <head>
        <title>ProductionEquityAI</title>
        <style>
          body {{ font-family: Arial, sans-serif; margin: 2rem; }}
          .modules {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; }}
          .card {{ border: 1px solid #ccc; border-radius: 8px; padding: 1rem; background: #fdfdfd; }}
          h1 {{ margin-top: 0; }}
          ul {{ padding-left: 1.25rem; }}
        </style>
      </head>
      <body>
        <h1>ProductionEquityAI Modules</h1>
        <p>Use this landing page to navigate to OpenAPI docs or hit module-specific endpoints.</p>
        <div class="modules">
          <div class="card"><h3>Module 1</h3><p>Ingestion & preprocessing</p><p><code>/module1/ingest</code></p></div>
          <div class="card"><h3>Module 2</h3><p>Valuation engine</p><p><code>/module2/valuation</code></p></div>
          <div class="card"><h3>Module 3</h3><p>ML modeling</p><p><code>/module3/signals</code></p></div>
          <div class="card"><h3>Module 4</h3><p>Backtesting</p><p><code>/module4/backtest</code></p></div>
          <div class="card"><h3>Module 5</h3><p>API catalog</p><p><code>/module5/summary</code></p></div>
          <div class="card"><h3>Module 7</h3><p>Observability</p><p><code>/module7/observability</code></p></div>
        </div>
        <h2>Tickers loaded</h2>
        <ul>{ticker_list}</ul>
        <p><a href="/docs">Explore the interactive API docs</a></p>
      </body>
    </html>
    """
    return html
