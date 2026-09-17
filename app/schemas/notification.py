from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class MerchantNotificationResponse(BaseModel):
    id: str
    merchant_id: str
    type: str
    title: str
    message: str
    related_insight_id: Optional[str] = None
    related_campaign_id: Optional[str] = None
    read: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerNotificationResponse(BaseModel):
    id: str
    customer_id: str
    campaign_id: str
    title: str
    message: str
    status: str
    sent_at: datetime
    read_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
