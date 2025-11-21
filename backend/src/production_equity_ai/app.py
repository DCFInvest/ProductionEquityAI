"""FastAPI application wiring all ProductionEquityAI modules."""
from fastapi import FastAPI

from .config import get_settings
from .logging_config import configure_logging
from .modules import module1, module2, module3, module4, module5, module6, module7


def build_app() -> FastAPI:
    """Create the FastAPI application and register module routers."""

    configure_logging()
    settings = get_settings()
    app = FastAPI(
        title="ProductionEquityAI",
        description=(
            "Unified service exposing Modules 1-7 for ingestion, valuation, ML, "
            "analytics, and operations."
        ),
        version="0.1.0",
    )

    @app.get("/health", summary="Service health")
    def health() -> dict:
        return {
            "status": "ok",
            "database_url": settings.database_url,
            "modules": list(range(1, 8)),
        }

    app.include_router(module1.router, prefix="/module1", tags=["module1"])
    app.include_router(module2.router, prefix="/module2", tags=["module2"])
    app.include_router(module3.router, prefix="/module3", tags=["module3"])
    app.include_router(module4.router, prefix="/module4", tags=["module4"])
    app.include_router(module5.router, prefix="/module5", tags=["module5"])
    app.include_router(module6.router, prefix="/module6", tags=["module6"])
    app.include_router(module7.router, prefix="/module7", tags=["module7"])

    return app


app = build_app()
