from app.database.models import Insight, Recommendation, Customer, CustomerSegment
from app.services.recommendation_service import RecommendationService
from app.services.campaign_service import CampaignService


def test_recommendation_and_campaign_approval_flow(db):
    # 1. Create test Insight
    insight = Insight(
        merchant_id="test_mer_001",
        type="sales_drop",
        title="Sales dropped 16%",
        summary="Slow window 4 PM - 7 PM",
        severity="medium",
        data={"revenue_change": -16, "inactive_regular_customers": 10},
        status="active"
    )
    db.add(insight)
    db.commit()

    # 2. Add sample target customers and segments
    cust = Customer(
        id="test_c1",
        merchant_id="test_mer_001",
        customer_reference="C-100",
        name="Test Inactive Cust",
        phone="+919999900001",
        total_transactions=3,
        total_spend=900.0
    )
    db.add(cust)
    seg = CustomerSegment(
        merchant_id="test_mer_001",
        customer_id="test_c1",
        segment="inactive_regular",
        score=0.9
    )
    db.add(seg)
    db.commit()

    # 3. Generate Recommendation
    rec = RecommendationService.generate_recommendation_for_insight(db, insight)
    assert rec.status == "pending"
    assert rec.target_segment == "inactive_regular"

    # 4. Approve Recommendation
    approve_res = RecommendationService.approve_recommendation(db, rec.id)
    assert approve_res.status == "approved"
    assert approve_res.campaign_name == rec.title
    assert approve_res.eligible_customers_count >= 1

    # 5. Measure Campaign
    camp_result = CampaignService.measure_campaign(db, approve_res.campaign_id)
    assert camp_result.targeted_count >= 1
    assert camp_result.revenue_generated > 0
    assert camp_result.roi > 0
