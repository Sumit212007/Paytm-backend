from datetime import datetime, timedelta
from app.database.models import Customer
from app.services.segmentation_service import SegmentationService


def test_customer_classification():
    now = datetime.utcnow()

    # New Customer
    new_cust = Customer(
        customer_reference="C1", name="New", phone="123",
        first_purchase_at=now, last_purchase_at=now,
        total_transactions=1, total_spend=150.0
    )
    seg, score, reason = SegmentationService.classify_customer(new_cust)
    assert seg == "new_customer"

    # Regular Customer
    reg_cust = Customer(
        customer_reference="C2", name="Reg", phone="124",
        first_purchase_at=now - timedelta(days=20),
        last_purchase_at=now - timedelta(days=2),
        total_transactions=3, total_spend=600.0
    )
    seg, score, reason = SegmentationService.classify_customer(reg_cust)
    assert seg == "regular_customer"

    # Inactive Regular
    inact_cust = Customer(
        customer_reference="C3", name="Inact", phone="125",
        first_purchase_at=now - timedelta(days=90),
        last_purchase_at=now - timedelta(days=45),
        total_transactions=4, total_spend=900.0
    )
    seg, score, reason = SegmentationService.classify_customer(inact_cust)
    assert seg == "inactive_regular"

    # High Value Customer
    hv_cust = Customer(
        customer_reference="C4", name="HighVal", phone="126",
        first_purchase_at=now - timedelta(days=30),
        last_purchase_at=now - timedelta(days=1),
        total_transactions=5, total_spend=2500.0
    )
    seg, score, reason = SegmentationService.classify_customer(hv_cust)
    assert seg == "high_value_customer"
