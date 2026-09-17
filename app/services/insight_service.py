from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.models import Insight, Merchant
from app.services.anomaly_service import AnomalyService
from app.services.ai_service import AIService
from app.services.notification_service import NotificationService
from app.core.logging import logger


class InsightService:
    @staticmethod
    def analyze_and_generate_insights(db: Session, merchant_id: str, force: bool = False) -> List[Insight]:
        merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
        if not merchant:
            raise ValueError(f"Merchant with ID '{merchant_id}' not found.")

        lang = merchant.language_preference or "hinglish"
        ai_service = AIService()

        detected = AnomalyService.detect_anomalies(db, merchant_id)
        created_insights = []

        for item in detected:
            type_ = item["type"]
            data = item["data"]

            # Check if active insight exists
            existing = db.query(Insight).filter(
                Insight.merchant_id == merchant_id,
                Insight.type == type_,
                Insight.status == "active"
            ).first()

            if existing and not force:
                created_insights.append(existing)
                continue

            # Generate natural language explanation using AI service
            ai_exp = ai_service.explain_insight(data, language=lang)

            insight = Insight(
                merchant_id=merchant_id,
                type=type_,
                title=ai_exp.get("title", item["title"]),
                summary=f"{ai_exp.get('explanation', item['summary'])} {ai_exp.get('opportunity', '')}",
                severity=item.get("severity", "medium"),
                data=data,
                status="active",
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
            db.add(insight)
            db.commit()
            db.refresh(insight)

            # Create Merchant Notification
            NotificationService.create_merchant_notification(
                db=db,
                merchant_id=merchant_id,
                type_="new_insight",
                title=insight.title,
                message=insight.summary,
                related_insight_id=insight.id
            )

            created_insights.append(insight)

        return created_insights
