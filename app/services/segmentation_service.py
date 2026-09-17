from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.database.models import Customer, CustomerSegment
from app.core.logging import logger


class SegmentationConfig:
    """Configurable thresholds for customer segmentation."""
    NEW_CUSTOMER_MAX_TX: int = 1
    REGULAR_MIN_TX: int = 2
    LOYAL_MIN_TX: int = 5
    INACTIVE_DAYS: int = 30
    HIGH_VALUE_MIN_SPEND: float = 1000.0


class SegmentationService:
    @staticmethod
    def classify_customer(
        customer: Customer,
        config: SegmentationConfig = SegmentationConfig()
    ) -> Tuple[str, float, str]:
        now = datetime.utcnow()
        days_since_last = (now - customer.last_purchase_at).days if customer.last_purchase_at else 999

        # Rule 1: High Value Customer (spend above threshold)
        if customer.total_spend >= config.HIGH_VALUE_MIN_SPEND and customer.total_transactions >= config.REGULAR_MIN_TX:
            if days_since_last >= config.INACTIVE_DAYS:
                return "inactive_regular", 0.8, f"High value customer with spend ₹{customer.total_spend:.2f} but no purchases in {days_since_last} days."
            return "high_value_customer", 1.0, f"High value customer with total spend ₹{customer.total_spend:.2f} across {customer.total_transactions} orders."

        # Rule 2: Inactive Regular Customer
        if customer.total_transactions >= config.REGULAR_MIN_TX and days_since_last >= config.INACTIVE_DAYS:
            return "inactive_regular", 0.9, f"Customer made {customer.total_transactions} orders previously, but has been inactive for {days_since_last} days."

        # Rule 3: Loyal Customer
        if customer.total_transactions >= config.LOYAL_MIN_TX and days_since_last < config.INACTIVE_DAYS:
            return "loyal_customer", 1.0, f"Loyal repeat buyer with {customer.total_transactions} completed transactions."

        # Rule 4: Regular Customer
        if customer.total_transactions >= config.REGULAR_MIN_TX and days_since_last < config.INACTIVE_DAYS:
            return "regular_customer", 0.8, f"Regular buyer with {customer.total_transactions} transactions."

        # Rule 5: New Customer
        return "new_customer", 0.5, f"New customer with {customer.total_transactions} transaction."

    @staticmethod
    def update_merchant_customer_segments(
        db: Session,
        merchant_id: str,
        config: SegmentationConfig = SegmentationConfig()
    ) -> List[CustomerSegment]:
        customers = db.query(Customer).filter(Customer.merchant_id == merchant_id).all()
        updated_segments = []

        for cust in customers:
            segment_name, score, reason = SegmentationService.classify_customer(cust, config)

            # Check existing segment entry
            seg_entry = db.query(CustomerSegment).filter(
                CustomerSegment.merchant_id == merchant_id,
                CustomerSegment.customer_id == cust.id
            ).first()

            if seg_entry:
                seg_entry.segment = segment_name
                seg_entry.score = score
                seg_entry.reason = reason
            else:
                seg_entry = CustomerSegment(
                    merchant_id=merchant_id,
                    customer_id=cust.id,
                    segment=segment_name,
                    score=score,
                    reason=reason
                )
                db.add(seg_entry)

            updated_segments.append(seg_entry)

        db.commit()
        logger.info(f"Updated {len(updated_segments)} customer segments for merchant {merchant_id}.")
        return updated_segments
