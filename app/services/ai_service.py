from typing import Dict, Any, Optional
from app.integrations.gemini.client import GeminiClient
from app.core.logging import logger


class AIService:
    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        self.gemini = gemini_client or GeminiClient()

    def explain_insight(self, insight_data: Dict[str, Any], language: str = "hinglish") -> Dict[str, Any]:
        """
        Uses Gemini to generate a natural language explanation of an anomaly/insight.
        Supports English, Hindi, and Hinglish.
        """
        prompt = f"""
Given the following business anomaly data:
{insight_data}

Generate a clear, helpful merchant explanation in language '{language}'.
Language Rules:
- If language is 'english': write standard clear English.
- If language is 'hindi': write Devanagari Hindi.
- If language is 'hinglish': write natural conversational Roman Hindi (Hinglish), keeping business terms (sales, revenue, campaign, customers, offer, ROI) in English.

Return strict JSON only in this exact structure:
{{
  "title": "short concise title",
  "explanation": "clear explanation of WHY this happened",
  "opportunity": "what growth opportunity exists",
  "recommended_action": "brief summary of next action"
}}
"""
        result = self.gemini.generate_json(prompt)
        if result and "explanation" in result:
            return result

        # Fallback deterministic responses if Gemini API key not present or call fails
        rev_change = insight_data.get("revenue_change", -16.0)
        weak_period = insight_data.get("weak_period", "4 PM - 7 PM")
        inactive_cust = insight_data.get("inactive_regular_customers", 137)

        if language == "hindi":
            return {
                "title": f"बिक्री में {abs(rev_change):.0f}% की गिरावट दर्ज की गई",
                "explanation": f"सबसे बड़ी गिरावट {weak_period} के दौरान हुई है।",
                "opportunity": f"{inactive_cust} नियमित ग्राहक पिछले 30 दिनों से निष्क्रिय हैं।",
                "recommended_action": "निष्क्रिय ग्राहकों को वापस लाने के लिए एक विशेष ऑफर अभियान चलाएं।"
            }
        elif language == "english":
            return {
                "title": f"Sales dropped by {abs(rev_change):.0f}%",
                "explanation": f"The biggest decline occurred between {weak_period}.",
                "opportunity": f"{inactive_cust} regular customers have become inactive recently.",
                "recommended_action": "Create a targeted win-back offer for inactive regular customers."
            }
        else:  # hinglish default
            return {
                "title": f"Sales {abs(rev_change):.0f}% kam hui hain",
                "explanation": f"Subse badi decline {weak_period} ke beech hui hai.",
                "opportunity": f"{inactive_cust} regular customers inactive ho gaye hain.",
                "recommended_action": "Inactive regular customers ke liye ek targeted win-back offer launch karein."
            }

    def generate_recommendation_campaign(self, insight_data: Dict[str, Any], language: str = "hinglish") -> Dict[str, Any]:
        """
        Generates a recommended campaign structure based on detected insight.
        """
        prompt = f"""
You are Paytm GrowthPilot AI.
Based on this business insight:
{insight_data}

Generate a structured campaign recommendation in language '{language}'.
Return strict JSON only matching this schema:
{{
  "type": "win_back",
  "title": "Win back inactive customers",
  "description": "Offer ₹50 OFF on orders above ₹300 during evening hours to bring back inactive regulars.",
  "target_segment": "inactive_regular",
  "offer_type": "flat_discount",
  "offer_value": 50.0,
  "minimum_order_value": 300.0,
  "recommended_time_start": "16:00",
  "recommended_time_end": "19:00",
  "duration_days": 3,
  "estimated_revenue": 18500.0,
  "reason": "Targeting 137 inactive regular customers during slow evening hours will drive repeat orders."
}}
"""
        result = self.gemini.generate_json(prompt)
        if result and "offer_type" in result:
            return result

        # Fallback recommendation matching section 32 specification
        return {
            "type": "win_back",
            "title": "Win back inactive regular customers",
            "description": "₹50 OFF above ₹300 valid between 4 PM – 7 PM for 3 days.",
            "target_segment": "inactive_regular",
            "offer_type": "flat_discount",
            "offer_value": 50.0,
            "minimum_order_value": 300.0,
            "recommended_time_start": "16:00",
            "recommended_time_end": "19:00",
            "duration_days": 3,
            "estimated_revenue": 18500.0,
            "reason": "Inactive regular customers can be encouraged to return during the weak evening period."
        }

    def chat_response(
        self,
        merchant_name: str,
        user_message: str,
        metrics_context: Dict[str, Any],
        recent_insights: list,
        language: str = "hinglish"
    ) -> Dict[str, Any]:
        """
        Interactive AI assistant response engine.
        """
        prompt = f"""
You are Paytm GrowthPilot, the AI Business Partner for Paytm Merchant '{merchant_name}'.
Language Preference: {language}
Language Rules:
- If 'hinglish': converse in friendly Roman Hindi, keeping business words (sales, revenue, campaign, customers, offer, ROI) in English.
- If 'hindi': use formal Devanagari Hindi.
- If 'english': use standard English.

Current Business Context:
- Today Revenue: ₹{metrics_context.get('today_revenue', 0)} ({metrics_context.get('today_transactions', 0)} orders)
- Yesterday Revenue: ₹{metrics_context.get('yesterday_revenue', 0)}
- Revenue Change: {metrics_context.get('revenue_change_percentage', 0)}%
- Inactive Regular Customers: {metrics_context.get('inactive_regular_customers_count', 0)}
- Recent Insights: {recent_insights}

User Merchant Question: "{user_message}"

Respond strictly as JSON:
{{
  "message": "Friendly response answering the user question using business metrics context",
  "related_insight_id": "optional_id_if_relevant",
  "suggested_action": {{
    "type": "view_recommendation",
    "id": "rec_id_if_any"
  }}
}}
"""
        result = self.gemini.generate_json(prompt)
        if result and "message" in result:
            msg = result.get("message")
            return {
                "message": msg,
                "language": language,
                "related_insight_id": result.get("related_insight_id"),
                "suggested_action": result.get("suggested_action"),
                "text": msg,
                "audio_ready": True
            }

        # Fallback intelligent responses based on intent keyword matching if Gemini API key not present
        msg_lower = user_message.lower()
        if "sales" in msg_lower or "revenue" in msg_lower or "kam" in msg_lower or "drop" in msg_lower or "kyu" in msg_lower or "kyun" in msg_lower:
            rev_change = metrics_context.get('revenue_change_percentage', -15.92)
            if language == "hindi":
                text_out = f"आज आपकी बिक्री {abs(rev_change):.1f}% कम हुई है। मुख्य रूप से शाम 4 बजे से 7 बजे के बीच गिरावट आई है।"
            elif language == "english":
                text_out = f"Today your sales dropped by {abs(rev_change):.1f}%. Most of the decline happened between 4 PM and 7 PM."
            else:
                text_out = f"Aaj aapki sales main 4 PM–7 PM ke beech kam hui hain ({abs(rev_change):.1f}% decline)."

            return {
                "message": text_out,
                "language": language,
                "related_insight_id": recent_insights[0].get("id") if recent_insights else None,
                "suggested_action": {
                    "type": "view_recommendation",
                    "id": "rec_winback_001"
                },
                "text": text_out,
                "audio_ready": True
            }
        elif "inactive" in msg_lower or "customers" in msg_lower or "grahak" in msg_lower:
            inact = metrics_context.get('inactive_regular_customers_count', 137)
            if language == "hindi":
                text_out = f"आपके पास {inact} नियमित ग्राहक हैं जिन्होंने 30 दिनों से खरीदारी नहीं की है।"
            elif language == "english":
                text_out = f"You currently have {inact} regular customers who have been inactive for over 30 days."
            else:
                text_out = f"Aapke paas total {inact} inactive regular customers hain jinhone past 30 days se shopping nahi ki."

            return {
                "message": text_out,
                "language": language,
                "suggested_action": {
                    "type": "view_recommendation",
                    "id": "rec_winback_001"
                },
                "text": text_out,
                "audio_ready": True
            }
        else:
            if language == "hindi":
                text_out = f"नमस्कार! मैं Paytm GrowthPilot हूँ। आपकी बिक्री ₹{metrics_context.get('today_revenue', 0)} रही है। मैं आपकी दुकान बढ़ाने में क्या मदद कर सकता हूँ?"
            elif language == "english":
                text_out = f"Hello! I am your Paytm GrowthPilot. Today's store revenue is ₹{metrics_context.get('today_revenue', 0)}. How can I help grow your business today?"
            else:
                text_out = f"Namaste! Main aapka Paytm GrowthPilot assistant hoon. Today's revenue is ₹{metrics_context.get('today_revenue', 0)}. Aapki sales badhane ke liye main recommendations launch kar sakta hoon."

            return {
                "message": text_out,
                "language": language,
                "suggested_action": {
                    "type": "view_recommendation",
                    "id": "rec_winback_001"
                },
                "text": text_out,
                "audio_ready": True
            }
