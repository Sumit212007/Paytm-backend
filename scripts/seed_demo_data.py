import sys
import os
from datetime import datetime, timedelta
import random

# Add root project path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.connection import init_db, SessionLocal
from app.database.models import (
    Merchant, Customer, Transaction, CustomerSegment, BusinessMetric,
    Insight, Recommendation, MerchantNotification
)
from app.services.segmentation_service import SegmentationService
from app.core.logging import logger


def seed_demo_data():
    logger.info("Initializing database schema for seeding...")
    init_db()

    db = SessionLocal()

    try:
        # 1. Clean existing demo data if present
        existing_merchant = db.query(Merchant).filter(Merchant.id == "mer_sharma_001").first()
        if existing_merchant:
            logger.info("Cleaning previous demo data for mer_sharma_001...")
            db.delete(existing_merchant)
            db.commit()

        logger.info("Creating Merchant: Sharma General Store...")
        merchant = Merchant(
            id="mer_sharma_001",
            name="Ramesh Sharma",
            business_name="Sharma General Store",
            business_type="Grocery & General Store",
            location="Connaught Place, New Delhi",
            phone="+919876543210",
            language_preference="hinglish",
            timezone="Asia/Kolkata"
        )
        db.add(merchant)
        db.commit()

        # 2. Seed Customers
        # Generate 200 total customers, with 137 specifically tagged as inactive regulars
        logger.info("Seeding customers...")
        customers = []

        now = datetime.utcnow()

        # 137 Inactive Regular Customers (last purchase > 30 days ago, total_transactions >= 2)
        for i in range(1, 138):
            c_id = f"cust_inactive_{i:03d}"
            c_ref = f"CUST-INACT-{i:03d}"
            last_p = now - timedelta(days=random.randint(32, 60))
            first_p = last_p - timedelta(days=random.randint(30, 90))
            cust = Customer(
                id=c_id,
                merchant_id=merchant.id,
                customer_reference=c_ref,
                name=f"Customer {i}",
                phone=f"+9198100{i:05d}",
                first_purchase_at=first_p,
                last_purchase_at=last_p,
                total_transactions=random.randint(3, 8),
                total_spend=float(random.randint(1200, 4500))
            )
            customers.append(cust)
            db.add(cust)

        # 40 Regular / Active Customers
        for i in range(138, 178):
            c_id = f"cust_reg_{i:03d}"
            c_ref = f"CUST-REG-{i:03d}"
            last_p = now - timedelta(days=random.randint(1, 5))
            first_p = last_p - timedelta(days=random.randint(30, 120))
            cust = Customer(
                id=c_id,
                merchant_id=merchant.id,
                customer_reference=c_ref,
                name=f"Regular Customer {i}",
                phone=f"+9198200{i:05d}",
                first_purchase_at=first_p,
                last_purchase_at=last_p,
                total_transactions=random.randint(4, 15),
                total_spend=float(random.randint(2000, 8000))
            )
            customers.append(cust)
            db.add(cust)

        # 23 New Customers (1 transaction, < 10 days ago)
        for i in range(178, 201):
            c_id = f"cust_new_{i:03d}"
            c_ref = f"CUST-NEW-{i:03d}"
            last_p = now - timedelta(days=random.randint(0, 7))
            cust = Customer(
                id=c_id,
                merchant_id=merchant.id,
                customer_reference=c_ref,
                name=f"New Customer {i}",
                phone=f"+9198300{i:05d}",
                first_purchase_at=last_p,
                last_purchase_at=last_p,
                total_transactions=1,
                total_spend=float(random.randint(150, 600))
            )
            customers.append(cust)
            db.add(cust)

        db.commit()

        # 3. Seed Transactions
        # Generate transactions reflecting the ~16% revenue drop and 4 PM - 7 PM slow hours
        logger.info("Generating transactions with intentional revenue drop and slow evening hours...")
        categories = ["dairy", "groceries", "packaged_food", "personal_care", "beverages"]
        payment_methods = ["paytm_qr", "upi", "card", "cash"]

        # Generate transactions for the last 14 days
        for day_offset in range(14, -1, -1):
            target_date = now - timedelta(days=day_offset)

            # Baseline revenue per day: ~₹14,000 for days 14..8 (last week)
            # Declining revenue: ~₹11,700 for days 7..0 (this week) -> ~16% decline!
            is_decline_period = (day_offset <= 7)

            daily_target_tx_count = random.randint(30, 40) if not is_decline_period else random.randint(22, 30)

            for _ in range(daily_target_tx_count):
                # Pick transaction hour
                # Intentionally make 16:00 - 19:00 (4 PM - 7 PM) underperform significantly in decline period
                if is_decline_period and random.random() < 0.7:
                    # Pick morning 09-13 or late night 19-21
                    hour = random.choice([8, 9, 10, 11, 12, 13, 14, 15, 20, 21])
                else:
                    hour = random.randint(8, 21)

                tx_time = datetime(
                    target_date.year, target_date.month, target_date.day,
                    hour, random.randint(0, 59), random.randint(0, 59)
                )

                cust = random.choice(customers[137:])  # Pick active customers
                amount = float(random.choice([80, 150, 250, 320, 450, 600, 850]))

                tx = Transaction(
                    merchant_id=merchant.id,
                    customer_id=cust.id,
                    amount=amount,
                    transaction_time=tx_time,
                    payment_method=random.choice(payment_methods),
                    category=random.choice(categories)
                )
                db.add(tx)

        db.commit()

        # 4. Classify Customer Segments
        logger.info("Updating customer segments...")
        SegmentationService.update_merchant_customer_segments(db, merchant.id)

        # 5. Create Initial Insight (Sales Drop 16% & 137 Inactive Regular Customers)
        logger.info("Seeding initial detected business insight...")
        insight = Insight(
            id="ins_sales_drop_001",
            merchant_id=merchant.id,
            type="sales_drop",
            title="Sales dropped 16% this week",
            summary="The biggest decline happened between 4 PM and 7 PM. 137 regular customers have become inactive.",
            severity="high",
            data={
                "revenue_change": -15.92,
                "previous_revenue": 98000.0,
                "current_revenue": 82400.0,
                "weak_period": "4 PM - 7 PM",
                "inactive_regular_customers": 137
            },
            status="active",
            expires_at=now + timedelta(days=7)
        )
        db.add(insight)
        db.commit()

        # 6. Create Pending Recommendation
        logger.info("Seeding pending recommendation for merchant approval...")
        rec = Recommendation(
            id="rec_winback_001",
            merchant_id=merchant.id,
            insight_id=insight.id,
            type="win_back",
            title="Win back inactive regular customers",
            description="Offer ₹50 OFF above ₹300 valid between 4 PM – 7 PM for 3 days.",
            target_segment="inactive_regular",
            offer_type="flat_discount",
            offer_value=50.0,
            minimum_order_value=300.0,
            recommended_time_start="16:00",
            recommended_time_end="19:00",
            duration_days=3,
            estimated_revenue=18500.0,
            reason="Inactive regular customers can be encouraged to return during the weak evening period.",
            ai_generated=True,
            status="pending"
        )
        db.add(rec)

        # 7. Seed Initial Merchant Notification
        notif = MerchantNotification(
            merchant_id=merchant.id,
            type="new_recommendation",
            title="GrowthPilot Opportunity Detected",
            message="Sales dropped 16%. GrowthPilot recommends launching a ₹50 OFF win-back campaign for 137 inactive customers.",
            related_insight_id=insight.id,
            read=False
        )
        db.add(notif)
        db.commit()

        logger.info("Demo data successfully seeded for Sharma General Store!")
        logger.info("Summary of seeded data:")
        logger.info("- Merchant: Sharma General Store (ID: mer_sharma_001)")
        logger.info("- Total Customers: 200 (137 Inactive Regulars, 40 Regulars, 23 New)")
        logger.info("- Detected Insight: Sales dropped 16% (Weak window: 4 PM - 7 PM)")
        logger.info("- Pending Recommendation: Win back inactive regular customers (ID: rec_winback_001)")

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding demo data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
