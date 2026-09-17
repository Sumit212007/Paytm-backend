from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class TodayStats(BaseModel):
    revenue: float
    transactions: int
    change_percentage: float


class ActiveInsight(BaseModel):
    id: str
    title: str
    summary: str
    severity: str
    type: str


class ActiveRecommendation(BaseModel):
    id: str
    title: str
    target_segment: str
    target_count: int
    offer_type: str
    offer_value: float
    estimated_revenue: float


class RecentCampaign(BaseModel):
    id: str
    name: str
    status: str
    target_segment: str
    launched_at: Optional[str] = None


class DashboardResponse(BaseModel):
    merchant: Dict[str, Any]
    today: TodayStats
    active_insight: Optional[ActiveInsight] = None
    recommendation: Optional[ActiveRecommendation] = None
    recent_campaigns: List[RecentCampaign] = []
    unread_notifications: int = 0
