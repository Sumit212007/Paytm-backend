from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class CampaignBase(BaseModel):
    merchant_id: str
    recommendation_id: Optional[str] = None
    name: str
    campaign_type: str
    target_segment: str
    offer_type: str
    offer_value: float
    minimum_order_value: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_days: int = 3
    status: str = "draft"


class CampaignCreate(CampaignBase):
    pass


class CampaignResponse(CampaignBase):
    id: str
    approved_at: Optional[datetime] = None
    launched_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CampaignResultResponse(BaseModel):
    id: str
    campaign_id: str
    targeted_count: int
    delivered_count: int
    opened_count: int
    redeemed_count: int
    revenue_generated: float
    revenue_lift_percentage: float
    roi: float
    summary: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
