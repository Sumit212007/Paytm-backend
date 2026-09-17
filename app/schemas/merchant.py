from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class MerchantBase(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Sharma General Store"})
    business_name: str = Field(..., json_schema_extra={"example": "Sharma General Store"})
    business_type: str = Field(..., json_schema_extra={"example": "Grocery"})
    location: str = Field(..., json_schema_extra={"example": "Connaught Place, New Delhi"})
    phone: str = Field(..., json_schema_extra={"example": "+919876543210"})
    language_preference: str = Field("hinglish", json_schema_extra={"example": "hinglish"})
    timezone: str = Field("Asia/Kolkata", json_schema_extra={"example": "Asia/Kolkata"})


class MerchantCreate(MerchantBase):
    id: Optional[str] = None


class MerchantUpdate(BaseModel):
    name: Optional[str] = None
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    language_preference: Optional[str] = None
    timezone: Optional[str] = None


class MerchantResponse(MerchantBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
