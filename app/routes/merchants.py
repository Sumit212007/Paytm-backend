from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.merchant import MerchantResponse, MerchantUpdate, MerchantCreate
from app.services.merchant_service import MerchantService

router = APIRouter(prefix="/merchants", tags=["Merchants"])


@router.get("/{merchant_id}", response_model=MerchantResponse, summary="Get merchant profile")
def get_merchant(merchant_id: str, db: Session = Depends(get_db)):
    merchant = MerchantService.get_merchant(db, merchant_id)
    if not merchant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found")
    return merchant


@router.put("/{merchant_id}", response_model=MerchantResponse, summary="Update merchant profile & preferences")
def update_merchant(merchant_id: str, payload: MerchantUpdate, db: Session = Depends(get_db)):
    updated = MerchantService.update_merchant(db, merchant_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found")
    return updated
