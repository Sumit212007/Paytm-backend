from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Campaign, CampaignResult
from app.schemas.campaign import CampaignResponse, CampaignResultResponse
from app.services.campaign_service import CampaignService

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.get("", response_model=List[CampaignResponse], summary="List merchant campaigns")
def get_campaigns(merchant_id: str, db: Session = Depends(get_db)):
    return CampaignService.get_merchant_campaigns(db, merchant_id)


@router.get("/{campaign_id}", response_model=CampaignResponse, summary="Get campaign details by ID")
def get_campaign_by_id(campaign_id: str, db: Session = Depends(get_db)):
    camp = CampaignService.get_campaign(db, campaign_id)
    if not camp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    return camp


@router.post("/{campaign_id}/cancel", response_model=CampaignResponse, summary="Cancel an active campaign")
def cancel_campaign(campaign_id: str, db: Session = Depends(get_db)):
    try:
        return CampaignService.cancel_campaign(db, campaign_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{campaign_id}/results", response_model=CampaignResultResponse, summary="Get campaign performance results and ROI")
def get_campaign_results(campaign_id: str, db: Session = Depends(get_db)):
    res = db.query(CampaignResult).filter(CampaignResult.campaign_id == campaign_id).first()
    if not res:
        # If not measured yet, measure it on demand
        try:
            res = CampaignService.measure_campaign(db, campaign_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return res
