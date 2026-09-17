from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import Insight, CustomerSegment, Transaction
from app.services.analytics_service import AnalyticsService
from app.services.segmentation_service import SegmentationService
from app.core.logging import logger


class AnomalyService:
    """
    Rule-based anomaly and opportunity detection engine.
    Produces structured data for detected issues.
    """

    @staticmethod
    def detect_anomalies(db: Session, merchant_id: str) -> List[Dict[str, Any]]:
        # Ensure customer segments are fresh
        SegmentationService.update_merchant_customer_segments(db, merchant_id)

        overview = AnalyticsService.get_overview(db, merchant_id)
        hourly = AnalyticsService.get_hourly_analytics(db, merchant_id)
        cust_analytics = AnalyticsService.get_customer_analytics(db, merchant_id)

        detected_insights = []

        # 1. Sales Drop Detection (> 10% decline)
        if overview.revenue_change_percentage < -10.0:
            weak_window = ", ".join(hourly.slow_hours[:2]) if hourly.slow_hours else "4 PM - 7 PM"
            detected_insights.append({
                "type": "sales_drop",
                "title": f"Sales dropped by {abs(overview.revenue_change_percentage):.1f}%",
                "summary": f"Your business revenue experienced a decline compared to previous performance. The largest slowdown occurred during {weak_window}.",
                "severity": "high" if overview.revenue_change_percentage < -15.0 else "medium",
                "data": {
                    "revenue_change": overview.revenue_change_percentage,
                    "today_revenue": overview.today_revenue,
                    "yesterday_revenue": overview.yesterday_revenue,
                    "weak_period": weak_window,
                    "inactive_regular_customers": cust_analytics.inactive_regular_customers
                }
            })

        # 2. Slow Hours Window Opportunity
        if hourly.slow_hours:
            weak_window = hourly.slow_hours[0]
            detected_insights.append({
                "type": "slow_hours",
                "title": f"Underperforming hours detected ({weak_window})",
                "summary": f"Transaction volume dips significantly during {weak_window}. Running a flash offer can boost store footfall.",
                "severity": "medium",
                "data": {
                    "slow_hours_window": weak_window,
                    "peak_hours": hourly.peak_hours,
                    "suggested_time_start": "16:00",
                    "suggested_time_end": "19:00"
                }
            })

        # 3. Customer Inactivity Spike
        if cust_analytics.inactive_regular_customers > 0:
            detected_insights.append({
                "type": "customer_inactivity",
                "title": f"{cust_analytics.inactive_regular_customers} regular customers haven't returned recently",
                "summary": f"{cust_analytics.inactive_regular_customers} customers who used to shop regularly have not made a purchase in over 30 days.",
                "severity": "high" if cust_analytics.inactive_regular_customers > 50 else "medium",
                "data": {
                    "inactive_regular_customers": cust_analytics.inactive_regular_customers,
                    "total_customers": cust_analytics.total_customers,
                    "target_segment": "inactive_regular"
                }
            })

        logger.info(f"Detected {len(detected_insights)} anomalies/opportunities for merchant {merchant_id}.")
        return detected_insights
