from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Insight
from app.schemas.insight import InsightResponse, InsightAnalyzeRequest
from app.services.insight_service import InsightService

router = APIRouter(prefix="/insights", tags=["Insights"])


@router.get("", response_model=List[InsightResponse], summary="List merchant insights")
def get_insights(merchant_id: str, status_filter: str = "active", db: Session = Depends(get_db)):
    query = db.query(Insight).filter(Insight.merchant_id == merchant_id)
    if status_filter:
        query = query.filter(Insight.status == status_filter)
    return query.order_by(Insight.created_at.desc()).all()


@router.get("/{insight_id}", response_model=InsightResponse, summary="Get insight by ID")
def get_insight_by_id(insight_id: str, db: Session = Depends(get_db)):
    insight = db.query(Insight).filter(Insight.id == insight_id).first()
    if not insight:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insight not found")
    return insight


@router.post("/analyze", response_model=List[InsightResponse], summary="Trigger manual business anomaly analysis")
def analyze_merchant_data(payload: InsightAnalyzeRequest, db: Session = Depends(get_db)):
    return InsightService.analyze_and_generate_insights(db, payload.merchant_id, payload.force)
