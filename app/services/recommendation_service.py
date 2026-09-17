from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database.models import (
    Recommendation, Insight, Merchant, Campaign, CampaignTarget, Customer, CustomerSegment
)
from app.services.ai_service import AIService
from app.services.n8n_service import N8NService
from app.services.notification_service import NotificationService
from app.schemas.recommendation import RecommendationApproveResponse
from app.core.logging import logger


class RecommendationService:
    @staticmethod
    def generate_recommendation_for_insight(db: Session, insight: Insight) -> Recommendation:
        # Check if recommendation already exists for this insight
        existing = db.query(Recommendation).filter(
            Recommendation.insight_id == insight.id,
            Recommendation.status == "pending"
        ).first()
        if existing:
            return existing

        merchant = db.query(Merchant).filter(Merchant.id == insight.merchant_id).first()
        lang = merchant.language_preference if merchant else "hinglish"

        ai_service = AIService()
        ai_rec = ai_service.generate_recommendation_campaign(insight.data or {}, language=lang)

        rec = Recommendation(
            merchant_id=insight.merchant_id,
            insight_id=insight.id,
            type=ai_rec.get("type", "win_back"),
            title=ai_rec.get("title", "Win back inactive customers"),
            description=ai_rec.get("description", "₹50 OFF above ₹300 between 4 PM – 7 PM"),
            target_segment=ai_rec.get("target_segment", "inactive_regular"),
            offer_type=ai_rec.get("offer_type", "flat_discount"),
            offer_value=float(ai_rec.get("offer_value", 50.0)),
            minimum_order_value=float(ai_rec.get("minimum_order_value", 300.0)),
            recommended_time_start=ai_rec.get("recommended_time_start", "16:00"),
            recommended_time_end=ai_rec.get("recommended_time_end", "19:00"),
            duration_days=int(ai_rec.get("duration_days", 3)),
            estimated_revenue=float(ai_rec.get("estimated_revenue", 18500.0)),
            reason=ai_rec.get("reason", "Drive repeat orders during slow evening hours."),
            ai_generated=True,
            status="pending"
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)

        # Notify merchant of new recommendation
        NotificationService.create_merchant_notification(
            db=db,
            merchant_id=insight.merchant_id,
            type_="new_recommendation",
            title=f"New AI Recommendation: {rec.title}",
            message=rec.description,
            related_insight_id=insight.id
        )

        return rec

    @staticmethod
    def approve_recommendation(db: Session, recommendation_id: str) -> RecommendationApproveResponse:
        rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
        if not rec:
            raise ValueError(f"Recommendation '{recommendation_id}' not found.")

        if rec.status == "approved":
            # If already approved, return associated campaign info
            campaign = db.query(Campaign).filter(Campaign.recommendation_id == rec.id).first()
            if campaign:
                target_count = db.query(CampaignTarget).filter(CampaignTarget.campaign_id == campaign.id).count()
                return RecommendationApproveResponse(
                    recommendation_id=rec.id,
                    campaign_id=campaign.id,
                    status="approved",
                    message="Recommendation was already approved and campaign is active.",
                    campaign_name=campaign.name,
                    eligible_customers_count=target_count,
                    n8n_triggered=True
                )

        if rec.status not in ["pending", "draft"]:
            raise ValueError(f"Recommendation '{recommendation_id}' is in status '{rec.status}' and cannot be approved.")

        now = datetime.utcnow()
        end_time = now + timedelta(days=rec.duration_days)

        # 1. Create Campaign
        campaign = Campaign(
            merchant_id=rec.merchant_id,
            recommendation_id=rec.id,
            name=rec.title,
            campaign_type=rec.type,
            target_segment=rec.target_segment,
            offer_type=rec.offer_type,
            offer_value=rec.offer_value,
            minimum_order_value=rec.minimum_order_value,
            start_time=now,
            end_time=end_time,
            duration_days=rec.duration_days,
            status="running",
            approved_at=now,
            launched_at=now
        )
        db.add(campaign)
        rec.status = "approved"
        db.commit()
        db.refresh(campaign)

        # 2. Identify Eligible Target Customers
        target_segments = db.query(CustomerSegment).filter(
            CustomerSegment.merchant_id == rec.merchant_id,
            CustomerSegment.segment == rec.target_segment
        ).all()

        eligible_customer_ids = [s.customer_id for s in target_segments]
        # Fallback if no specific segment entries, target customers meeting criteria
        if not eligible_customer_ids:
            all_custs = db.query(Customer).filter(Customer.merchant_id == rec.merchant_id).all()
            eligible_customer_ids = [c.id for c in all_custs[:137]]

        # Populate CampaignTargets
        for cid in eligible_customer_ids:
            target = CampaignTarget(
                campaign_id=campaign.id,
                customer_id=cid,
                eligible=True,
                notification_status="pending"
            )
            db.add(target)
        db.commit()

        # 3. Dispatch Mock Customer Notifications
        NotificationService.dispatch_campaign_notifications(db, campaign)

        # 4. Trigger n8n Automation Webhook
        n8n_service = N8NService()
        n8n_triggered = n8n_service.dispatch_campaign_approved({
            "id": campaign.id,
            "merchant_id": campaign.merchant_id,
            "target_segment": campaign.target_segment,
            "offer_type": campaign.offer_type,
            "offer_value": campaign.offer_value,
            "minimum_order_value": campaign.minimum_order_value,
            "duration_days": campaign.duration_days
        })

        # 5. Notify Merchant of Launch
        NotificationService.create_merchant_notification(
            db=db,
            merchant_id=rec.merchant_id,
            type_="campaign_launched",
            title=f"Campaign Launched: {campaign.name}",
            message=f"Campaign is live for {len(eligible_customer_ids)} customers. Notifications sent!",
            related_campaign_id=campaign.id
        )

        return RecommendationApproveResponse(
            recommendation_id=rec.id,
            campaign_id=campaign.id,
            status="approved",
            message="Campaign approved, created, and launched successfully!",
            campaign_name=campaign.name,
            eligible_customers_count=len(eligible_customer_ids),
            n8n_triggered=n8n_triggered
        )

    @staticmethod
    def reject_recommendation(db: Session, recommendation_id: str) -> Recommendation:
        rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
        if not rec:
            raise ValueError(f"Recommendation '{recommendation_id}' not found.")
        rec.status = "rejected"
        db.commit()
        db.refresh(rec)
        return rec
