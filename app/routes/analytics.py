from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.analytics import (
    AnalyticsOverview, RevenueAnalytics, HourlyAnalytics, CustomerAnalytics
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverview, summary="Get high-level merchant analytics overview")
def get_analytics_overview(merchant_id: str, db: Session = Depends(get_db)):
    return AnalyticsService.get_overview(db, merchant_id)


@router.get("/revenue", response_model=RevenueAnalytics, summary="Get category revenue breakdown")
def get_revenue_analytics(merchant_id: str, period: str = "month", db: Session = Depends(get_db)):
    return AnalyticsService.get_revenue_by_category(db, merchant_id, period)


@router.get("/hourly", response_model=HourlyAnalytics, summary="Get hourly sales breakdown and peak/slow windows")
def get_hourly_analytics(merchant_id: str, db: Session = Depends(get_db)):
    return AnalyticsService.get_hourly_analytics(db, merchant_id)


@router.get("/customers", response_model=CustomerAnalytics, summary="Get customer breakdown by segments")
def get_customer_analytics(merchant_id: str, db: Session = Depends(get_db)):
    return AnalyticsService.get_customer_analytics(db, merchant_id)
