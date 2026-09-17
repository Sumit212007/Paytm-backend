from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Merchant, Insight, AIConversation
from app.schemas.assistant import ChatRequest, ChatResponse
from app.services.analytics_service import AnalyticsService
from app.services.ai_service import AIService

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])


@router.post("/chat", response_model=ChatResponse, summary="Conversational AI copilot chat interface")
def chat_with_assistant(payload: ChatRequest, db: Session = Depends(get_db)):
    merchant = db.query(Merchant).filter(Merchant.id == payload.merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found")

    lang = payload.language or merchant.language_preference or "hinglish"

    # Save User message to AI Conversation history
    user_conv = AIConversation(
        merchant_id=merchant.id,
        role="user",
        message=payload.message,
        language=lang
    )
    db.add(user_conv)
    db.commit()

    # Gather business context
    overview = AnalyticsService.get_overview(db, merchant.id)
    metrics_context = overview.model_dump()

    recent_insights = db.query(Insight).filter(
        Insight.merchant_id == merchant.id,
        Insight.status == "active"
    ).order_by(Insight.created_at.desc()).limit(3).all()

    insights_data = [
        {"id": i.id, "title": i.title, "summary": i.summary, "type": i.type}
        for i in recent_insights
    ]

    # Generate response via AIService
    ai_service = AIService()
    response_dict = ai_service.chat_response(
        merchant_name=merchant.name,
        user_message=payload.message,
        metrics_context=metrics_context,
        recent_insights=insights_data,
        language=lang
    )

    # Save Assistant response to AI Conversation history
    assistant_conv = AIConversation(
        merchant_id=merchant.id,
        role="assistant",
        message=response_dict["message"],
        language=lang
    )
    db.add(assistant_conv)
    db.commit()

    return ChatResponse(
        message=response_dict["message"],
        language=lang,
        related_insight_id=response_dict.get("related_insight_id"),
        related_campaign_id=response_dict.get("related_campaign_id"),
        suggested_action=response_dict.get("suggested_action"),
        audio_ready=True,
        text=response_dict["message"]
    )
