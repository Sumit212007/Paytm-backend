import json
import logging
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger("growthpilot.gemini")

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-generativeai package not installed.")


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.is_configured = False
        self.model = None

        if GENAI_AVAILABLE and self.api_key and self.api_key != "your-gemini-api-key-here" and len(self.api_key) > 5:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                self.is_configured = True
                logger.info("Gemini AI client successfully configured.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini AI client: {e}")

    def generate_text(self, prompt: str, system_instruction: str = None) -> Optional[str]:
        if not self.is_configured or not self.model:
            logger.info("Gemini API key not configured. Using fallback AI generator.")
            return None

        try:
            full_prompt = prompt
            if system_instruction:
                full_prompt = f"System Instructions: {system_instruction}\n\nUser Request: {prompt}"

            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API request failed: {e}")
            return None

    def generate_json(self, prompt: str, system_instruction: str = None) -> Optional[Dict[str, Any]]:
        raw_text = self.generate_text(prompt, system_instruction)
        if not raw_text:
            return None

        try:
            # Strip markdown json code block if present
            cleaned = raw_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"Failed to parse Gemini JSON output: {e}. Raw text: {raw_text}")
            return None
