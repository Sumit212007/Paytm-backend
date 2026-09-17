from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class InsightBase(BaseModel):
    merchant_id: str
    type: str
    title: str
    summary: str
    severity: str = "medium"
    data: Optional[Dict[str, Any]] = None
    status: str = "active"
    expires_at: Optional[datetime] = None


class InsightCreate(InsightBase):
    pass


class InsightResponse(InsightBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InsightAnalyzeRequest(BaseModel):
    merchant_id: str
    force: bool = False
