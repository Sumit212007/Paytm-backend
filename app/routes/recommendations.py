from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Recommendation, Insight
from app.schemas.recommendation import RecommendationResponse, RecommendationApproveResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("", response_model=List[RecommendationResponse], summary="List recommendations for a merchant")
def get_recommendations(merchant_id: str, status_filter: str = "pending", db: Session = Depends(get_db)):
    query = db.query(Recommendation).filter(Recommendation.merchant_id == merchant_id)
    if status_filter:
        query = query.filter(Recommendation.status == status_filter)
    return query.order_by(Recommendation.created_at.desc()).all()


@router.get("/{recommendation_id}", response_model=RecommendationResponse, summary="Get recommendation by ID")
def get_recommendation_by_id(recommendation_id: str, db: Session = Depends(get_db)):
    rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")
    return rec


@router.post("/{recommendation_id}/approve", response_model=RecommendationApproveResponse, summary="Approve a recommendation and launch campaign workflow")
def approve_recommendation(recommendation_id: str, db: Session = Depends(get_db)):
    try:
        return RecommendationService.approve_recommendation(db, recommendation_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{recommendation_id}/reject", response_model=RecommendationResponse, summary="Reject a recommendation")
def reject_recommendation(recommendation_id: str, db: Session = Depends(get_db)):
    try:
        return RecommendationService.reject_recommendation(db, recommendation_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
