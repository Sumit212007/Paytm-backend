from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class CustomerBase(BaseModel):
    customer_reference: str = Field(..., json_schema_extra={"example": "CUST-1001"})
    name: str = Field(..., json_schema_extra={"example": "Rahul Verma"})
    phone: str = Field(..., json_schema_extra={"example": "+919988776655"})


class CustomerCreate(CustomerBase):
    merchant_id: str


class CustomerResponse(CustomerBase):
    id: str
    merchant_id: str
    first_purchase_at: Optional[datetime] = None
    last_purchase_at: Optional[datetime] = None
    total_transactions: int = 0
    total_spend: float = 0.0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerSegmentResponse(BaseModel):
    id: str
    merchant_id: str
    customer_id: str
    customer_name: Optional[str] = None
    customer_reference: Optional[str] = None
    segment: str
    score: float
    reason: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
