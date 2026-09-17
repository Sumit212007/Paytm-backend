from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import MerchantNotification, CustomerNotification, Campaign, Customer, CampaignTarget
from app.core.logging import logger


class MockNotificationProvider:
    """
    Mock Paytm Customer Notification Provider for Hackathon Demo.
    Simulates SMS / Paytm App push notifications sent to targeted customers.
    """
    @staticmethod
    def send_customer_campaign_notification(
        customer_phone: str,
        title: str,
        message: str
    ) -> bool:
        logger.info(f"[MOCK PAYTM PUSH NOTIFICATION] Sent to {customer_phone}: '{title}' - {message}")
        return True


class NotificationService:
    @staticmethod
    def create_merchant_notification(
        db: Session,
        merchant_id: str,
        type_: str,
        title: str,
        message: str,
        related_insight_id: Optional[str] = None,
        related_campaign_id: Optional[str] = None
    ) -> MerchantNotification:
        notif = MerchantNotification(
            merchant_id=merchant_id,
            type=type_,
            title=title,
            message=message,
            related_insight_id=related_insight_id,
            related_campaign_id=related_campaign_id,
            read=False
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        logger.info(f"Created merchant notification '{title}' for merchant {merchant_id}.")
        return notif

    @staticmethod
    def dispatch_campaign_notifications(
        db: Session,
        campaign: Campaign
    ) -> int:
        """
        Finds eligible targets for a campaign and creates customer notifications.
        """
        targets = db.query(CampaignTarget).filter(
            CampaignTarget.campaign_id == campaign.id,
            CampaignTarget.eligible == True
        ).all()

        count = 0
        for target in targets:
            cust = db.query(Customer).filter(Customer.id == target.customer_id).first()
            if not cust:
                continue

            notif_title = f"Exclusive Paytm Offer from {campaign.name}"
            notif_msg = f"Get ₹{campaign.offer_value:.0f} OFF on orders above ₹{campaign.minimum_order_value:.0f}!"

            # Mock Push Dispatch
            MockNotificationProvider.send_customer_campaign_notification(
                customer_phone=cust.phone,
                title=notif_title,
                message=notif_msg
            )

            # Store in DB
            cust_notif = CustomerNotification(
                customer_id=cust.id,
                campaign_id=campaign.id,
                title=notif_title,
                message=notif_msg,
                status="delivered",
                sent_at=datetime.utcnow()
            )
            db.add(cust_notif)

            target.notification_status = "delivered"
            count += 1

        db.commit()
        logger.info(f"Dispatched {count} mock customer notifications for campaign {campaign.id}.")
        return count
