from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.transaction import TransactionResponse, TransactionCreate
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=List[TransactionResponse], summary="List merchant transactions")
def get_transactions(
    merchant_id: str,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    return TransactionService.get_merchant_transactions(db, merchant_id, limit, offset)


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED, summary="Record a new transaction")
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    return TransactionService.create_transaction(db, payload)
