from typing import Optional, List
from sqlalchemy.orm import Session
from app.database.models import Merchant
from app.schemas.merchant import MerchantCreate, MerchantUpdate


class MerchantService:
    @staticmethod
    def get_merchant(db: Session, merchant_id: str) -> Optional[Merchant]:
        return db.query(Merchant).filter(Merchant.id == merchant_id).first()

    @staticmethod
    def create_merchant(db: Session, data: MerchantCreate) -> Merchant:
        merchant = Merchant(
            id=data.id if data.id else None,
            name=data.name,
            business_name=data.business_name,
            business_type=data.business_type,
            location=data.location,
            phone=data.phone,
            language_preference=data.language_preference,
            timezone=data.timezone
        )
        db.add(merchant)
        db.commit()
        db.refresh(merchant)
        return merchant

    @staticmethod
    def update_merchant(db: Session, merchant_id: str, data: MerchantUpdate) -> Optional[Merchant]:
        merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
        if not merchant:
            return None

        update_dict = data.dict(exclude_unset=True)
        for field, val in update_dict.items():
            if val is not None:
                setattr(merchant, field, val)

        db.commit()
        db.refresh(merchant)
        return merchant
