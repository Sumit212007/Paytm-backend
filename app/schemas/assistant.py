from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    merchant_id: str = Field(..., json_schema_extra={"example": "mer_sharma_001"})
    message: str = Field(..., json_schema_extra={"example": "Aaj sales kam kyu hui?"})
    language: Optional[str] = None


class SuggestedAction(BaseModel):
    type: str
    id: Optional[str] = None
    title: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    language: str
    related_insight_id: Optional[str] = None
    related_campaign_id: Optional[str] = None
    suggested_action: Optional[SuggestedAction] = None
    audio_ready: bool = True
    text: Optional[str] = None


class VoiceResponse(BaseModel):
    text: str
    language: str
    audio_ready: bool = True
