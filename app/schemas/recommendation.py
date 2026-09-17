from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class RecommendationBase(BaseModel):
    merchant_id: str
    insight_id: Optional[str] = None
    type: str
    title: str
    description: str
    target_segment: str
    offer_type: str
    offer_value: float
    minimum_order_value: float = 0.0
    recommended_time_start: Optional[str] = "16:00"
    recommended_time_end: Optional[str] = "19:00"
    duration_days: int = 3
    estimated_revenue: float = 0.0
    reason: Optional[str] = None
    ai_generated: bool = True
    status: str = "pending"


class RecommendationCreate(RecommendationBase):
    pass


class RecommendationResponse(RecommendationBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecommendationApproveResponse(BaseModel):
    recommendation_id: str
    campaign_id: str
    status: str
    message: str
    campaign_name: str
    eligible_customers_count: int
    n8n_triggered: bool
