import logging
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger("growthpilot.n8n")


class N8NClient:
    def __init__(self):
        self.base_url = settings.N8N_BASE_URL
        self.campaign_webhook = settings.N8N_CAMPAIGN_WEBHOOK_URL
        self.analysis_webhook = settings.N8N_ANALYSIS_WEBHOOK_URL
        self.api_key = settings.N8N_API_KEY

    def trigger_campaign_webhook(self, campaign_payload: Dict[str, Any]) -> bool:
        """
        Sends campaign approval event payload to n8n webhook.
        """
        if not self.campaign_webhook:
            logger.info("N8N_CAMPAIGN_WEBHOOK_URL not configured. Simulating n8n trigger.")
            return True

        headers = {}
        if self.api_key:
            headers["X-N8N-API-KEY"] = self.api_key

        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.post(self.campaign_webhook, json=campaign_payload, headers=headers)
                logger.info(f"Triggered n8n campaign webhook. Status: {res.status_code}")
                return res.status_code in [200, 201, 202]
        except Exception as e:
            logger.warning(f"Could not reach n8n campaign webhook: {e}. Falling back to internal async handler.")
            return False

    def trigger_analysis_webhook(self, analysis_payload: Dict[str, Any]) -> bool:
        """
        Sends scheduled analysis trigger to n8n webhook.
        """
        if not self.analysis_webhook:
            logger.info("N8N_ANALYSIS_WEBHOOK_URL not configured. Simulating n8n analysis trigger.")
            return True

        headers = {}
        if self.api_key:
            headers["X-N8N-API-KEY"] = self.api_key

        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.post(self.analysis_webhook, json=analysis_payload, headers=headers)
                logger.info(f"Triggered n8n analysis webhook. Status: {res.status_code}")
                return res.status_code in [200, 201, 202]
        except Exception as e:
            logger.warning(f"Could not reach n8n analysis webhook: {e}.")
            return False
