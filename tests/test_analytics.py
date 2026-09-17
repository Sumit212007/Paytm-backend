from datetime import datetime, timedelta
from app.database.models import Customer, Transaction
from app.services.analytics_service import AnalyticsService
from app.utils.helpers import calculate_percentage_change


def test_percentage_change_calculation():
    assert calculate_percentage_change(100.0, 84.0) == -16.0
    assert calculate_percentage_change(100.0, 120.0) == 20.0
    assert calculate_percentage_change(0.0, 50.0) == 100.0


def test_analytics_overview_calculation(db):
    now = datetime.utcnow()
    # Add transaction for today
    tx1 = Transaction(
        merchant_id="test_mer_001",
        amount=500.0,
        transaction_time=now,
        payment_method="paytm_qr",
        category="groceries"
    )
    # Add transaction for yesterday
    tx2 = Transaction(
        merchant_id="test_mer_001",
        amount=1000.0,
        transaction_time=now - timedelta(days=1),
        payment_method="upi",
        category="dairy"
    )
    db.add_all([tx1, tx2])
    db.commit()

    overview = AnalyticsService.get_overview(db, "test_mer_001")
    assert overview.today_revenue == 500.0
    assert overview.yesterday_revenue == 1000.0
    assert overview.revenue_change_percentage == -50.0
    assert overview.average_order_value == 750.0


def test_hourly_analytics(db):
    now = datetime.utcnow()
    tx1 = Transaction(
        merchant_id="test_mer_001",
        amount=200.0,
        transaction_time=datetime(now.year, now.month, now.day, 16, 30, 0),
        payment_method="paytm_qr"
    )
    db.add(tx1)
    db.commit()

    hourly = AnalyticsService.get_hourly_analytics(db, "test_mer_001", target_date=now)
    assert len(hourly.hourly_data) == 24
    assert hourly.hourly_data[16].revenue == 200.0
