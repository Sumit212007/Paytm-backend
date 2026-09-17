from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.security import setup_cors
from app.database.connection import init_db, get_db

# Import API Routers
from app.routes import (
    merchants, customers, transactions, analytics,
    insights, recommendations, campaigns, notifications,
    assistant, settings as settings_route, automation, dashboard
)

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables...")
    init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI Business Partner for Paytm Merchants - Backend API Specification",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS setup
setup_cors(app)

# Include API v1 Routers
api_v1_prefix = settings.API_V1_STR
app.include_router(dashboard.router, prefix=api_v1_prefix)
app.include_router(merchants.router, prefix=api_v1_prefix)
app.include_router(customers.router, prefix=api_v1_prefix)
app.include_router(transactions.router, prefix=api_v1_prefix)
app.include_router(analytics.router, prefix=api_v1_prefix)
app.include_router(insights.router, prefix=api_v1_prefix)
app.include_router(recommendations.router, prefix=api_v1_prefix)
app.include_router(campaigns.router, prefix=api_v1_prefix)
app.include_router(notifications.router, prefix=api_v1_prefix)
app.include_router(assistant.router, prefix=api_v1_prefix)
app.include_router(settings_route.router, prefix=api_v1_prefix)
app.include_router(automation.router, prefix=api_v1_prefix)


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    db_status = "disconnected"
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    ai_configured = bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 5 and settings.GEMINI_API_KEY != "your-gemini-api-key-here")
    n8n_configured = bool(settings.N8N_BASE_URL)

    return {
        "status": "ok",
        "database": db_status,
        "ai": "configured" if ai_configured else "mock_fallback_mode",
        "n8n": "configured" if n8n_configured else "not_configured"
    }
