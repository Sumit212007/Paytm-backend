from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class TransactionCreate(BaseModel):
    merchant_id: str
    customer_id: Optional[str] = None
    amount: float = Field(..., gt=0, json_schema_extra={"example": 250.0})
    transaction_time: datetime = Field(default_factory=datetime.utcnow)
    payment_method: str = Field("paytm_qr", json_schema_extra={"example": "paytm_qr"})
    category: str = Field("general", json_schema_extra={"example": "groceries"})


class TransactionResponse(BaseModel):
    id: str
    merchant_id: str
    customer_id: Optional[str] = None
    amount: float
    transaction_time: datetime
    payment_method: str
    category: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
