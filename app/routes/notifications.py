from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import MerchantNotification, CustomerNotification
from app.schemas.notification import MerchantNotificationResponse, CustomerNotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/merchant", response_model=List[MerchantNotificationResponse], summary="List notifications for a merchant")
def get_merchant_notifications(merchant_id: str, unread_only: bool = False, db: Session = Depends(get_db)):
    query = db.query(MerchantNotification).filter(MerchantNotification.merchant_id == merchant_id)
    if unread_only:
        query = query.filter(MerchantNotification.read == False)
    return query.order_by(MerchantNotification.created_at.desc()).all()


@router.post("/{notification_id}/read", summary="Mark merchant notification as read")
def mark_notification_read(notification_id: str, db: Session = Depends(get_db)):
    notif = db.query(MerchantNotification).filter(MerchantNotification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    notif.read = True
    db.commit()
    return {"status": "ok", "message": "Notification marked as read"}


@router.get("/customer/{customer_id}", response_model=List[CustomerNotificationResponse], summary="List customer campaign notifications")
def get_customer_notifications(customer_id: str, db: Session = Depends(get_db)):
    return db.query(CustomerNotification).filter(
        CustomerNotification.customer_id == customer_id
    ).order_by(CustomerNotification.created_at.desc()).all()
