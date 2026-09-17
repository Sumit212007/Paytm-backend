from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.customer import CustomerResponse, CustomerSegmentResponse
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=List[CustomerResponse], summary="List customers for a merchant")
def list_customers(merchant_id: str, db: Session = Depends(get_db)):
    return CustomerService.get_merchant_customers(db, merchant_id)


@router.get("/segments", response_model=List[CustomerSegmentResponse], summary="Get customer segment classifications")
def get_customer_segments(merchant_id: str, db: Session = Depends(get_db)):
    segments = CustomerService.get_merchant_segments(db, merchant_id)
    result = []
    for s in segments:
        cust = s.customer
        result.append(CustomerSegmentResponse(
            id=s.id,
            merchant_id=s.merchant_id,
            customer_id=s.customer_id,
            customer_name=cust.name if cust else None,
            customer_reference=cust.customer_reference if cust else None,
            segment=s.segment,
            score=s.score,
            reason=s.reason,
            created_at=s.created_at
        ))
    return result


@router.get("/{customer_id}", response_model=CustomerResponse, summary="Get customer by ID")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    cust = CustomerService.get_customer(db, customer_id)
    if not cust:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return cust
