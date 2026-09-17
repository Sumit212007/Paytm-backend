from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Merchant, Insight, Recommendation, Campaign, MerchantNotification, CampaignTarget
from app.schemas.dashboard import (
    DashboardResponse, TodayStats, ActiveInsight, ActiveRecommendation, RecentCampaign
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/dashboard", tags=["Dashboard Aggregation"])


@router.get("/{merchant_id}", response_model=DashboardResponse, summary="Aggregated endpoint for merchant Home screen")
def get_dashboard_data(merchant_id: str, db: Session = Depends(get_db)):
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found")

    # Analytics Overview
    overview = AnalyticsService.get_overview(db, merchant_id)

    today_stats = TodayStats(
        revenue=overview.today_revenue,
        transactions=overview.today_transactions,
        change_percentage=overview.revenue_change_percentage
    )

    # Active Insight
    active_ins_db = db.query(Insight).filter(
        Insight.merchant_id == merchant_id,
        Insight.status == "active"
    ).order_by(Insight.created_at.desc()).first()

    active_insight = None
    if active_ins_db:
        active_insight = ActiveInsight(
            id=active_ins_db.id,
            title=active_ins_db.title,
            summary=active_ins_db.summary,
            severity=active_ins_db.severity,
            type=active_ins_db.type
        )

    # Active Pending Recommendation
    active_rec_db = db.query(Recommendation).filter(
        Recommendation.merchant_id == merchant_id,
        Recommendation.status == "pending"
    ).order_by(Recommendation.created_at.desc()).first()

    recommendation = None
    if active_rec_db:
        recommendation = ActiveRecommendation(
            id=active_rec_db.id,
            title=active_rec_db.title,
            target_segment=active_rec_db.target_segment,
            target_count=overview.inactive_regular_customers_count or 137,
            offer_type=active_rec_db.offer_type,
            offer_value=active_rec_db.offer_value,
            estimated_revenue=active_rec_db.estimated_revenue
        )

    # Recent Campaigns
    recent_camps_db = db.query(Campaign).filter(
        Campaign.merchant_id == merchant_id
    ).order_by(Campaign.created_at.desc()).limit(5).all()

    recent_campaigns = [
        RecentCampaign(
            id=c.id,
            name=c.name,
            status=c.status,
            target_segment=c.target_segment,
            launched_at=c.launched_at.strftime("%Y-%m-%d %H:%M") if c.launched_at else None
        )
        for c in recent_camps_db
    ]

    # Unread Notifications
    unread_count = db.query(MerchantNotification).filter(
        MerchantNotification.merchant_id == merchant_id,
        MerchantNotification.read == False
    ).count()

    merchant_dict = {
        "id": merchant.id,
        "name": merchant.name,
        "business_name": merchant.business_name,
        "business_type": merchant.business_type,
        "location": merchant.location,
        "language_preference": merchant.language_preference
    }

    return DashboardResponse(
        merchant=merchant_dict,
        today=today_stats,
        active_insight=active_insight,
        recommendation=recommendation,
        recent_campaigns=recent_campaigns,
        unread_notifications=unread_count
    )
