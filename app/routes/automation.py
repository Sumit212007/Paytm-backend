from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Insight, Recommendation
from app.schemas.insight import InsightResponse
from app.schemas.campaign import CampaignResultResponse
from app.services.insight_service import InsightService
from app.services.recommendation_service import RecommendationService
from app.services.campaign_service import CampaignService

router = APIRouter(prefix="/automation", tags=["Automation & n8n"])


@router.post("/analyze/{merchant_id}", response_model=List[InsightResponse], summary="n8n webhook endpoint to trigger merchant data analysis")
def automation_analyze_merchant(merchant_id: str, db: Session = Depends(get_db)):
    """
    Called by n8n scheduled workflow or manual trigger.
    Runs anomaly detection, calls Gemini for explanations & recommendation generation, and saves notifications.
    """
    try:
        insights = InsightService.analyze_and_generate_insights(db, merchant_id, force=True)
        # For each new insight, ensure recommendation is generated
        for ins in insights:
            RecommendationService.generate_recommendation_for_insight(db, ins)
        return insights
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/measure-campaign/{campaign_id}", response_model=CampaignResultResponse, summary="n8n webhook endpoint to measure campaign results")
def automation_measure_campaign(campaign_id: str, db: Session = Depends(get_db)):
    """
    Called by n8n or scheduled worker to evaluate completed campaign revenue, redemptions, and ROI.
    """
    try:
        return CampaignService.measure_campaign(db, campaign_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
