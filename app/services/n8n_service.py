from typing import Dict, Any, Optional
from app.integrations.n8n.client import N8NClient
from app.core.logging import logger


class N8NService:
    def __init__(self, n8n_client: Optional[N8NClient] = None):
        self.client = n8n_client or N8NClient()

    def dispatch_campaign_approved(self, campaign_data: Dict[str, Any]) -> bool:
        """
        Dispatches campaign data to n8n workflow upon merchant approval.
        """
        payload = {
            "event": "campaign_approved",
            "campaign_id": campaign_data.get("id"),
            "merchant_id": campaign_data.get("merchant_id"),
            "target_segment": campaign_data.get("target_segment"),
            "offer_type": campaign_data.get("offer_type"),
            "offer_value": campaign_data.get("offer_value"),
            "minimum_order_value": campaign_data.get("minimum_order_value"),
            "duration_days": campaign_data.get("duration_days")
        }
        return self.client.trigger_campaign_webhook(payload)

    def dispatch_periodic_analysis(self, merchant_id: str) -> bool:
        """
        Dispatches scheduled periodic analysis trigger to n8n.
        """
        payload = {
            "event": "periodic_analysis_requested",
            "merchant_id": merchant_id
        }
        return self.client.trigger_analysis_webhook(payload)
