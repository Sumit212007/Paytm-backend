import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Paytm GrowthPilot Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./growthpilot.db"
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None

    # AI
    GEMINI_API_KEY: Optional[str] = None

    # n8n
    N8N_BASE_URL: str = "http://localhost:5678"
    N8N_CAMPAIGN_WEBHOOK_URL: Optional[str] = "http://localhost:5678/webhook/growthpilot-campaign"
    N8N_ANALYSIS_WEBHOOK_URL: Optional[str] = "http://localhost:5678/webhook/growthpilot-analysis"
    N8N_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
