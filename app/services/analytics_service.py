from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.database.models import Transaction, Customer, CustomerSegment
from app.utils.helpers import get_date_range_for_period, calculate_percentage_change
from app.schemas.analytics import (
    AnalyticsOverview, HourlyAnalytics, HourlyBucket,
    RevenueAnalytics, CategoryRevenue, CustomerAnalytics
)


class AnalyticsService:
    @staticmethod
    def get_overview(db: Session, merchant_id: str) -> AnalyticsOverview:
        now = datetime.utcnow()
        today_start, today_end = get_date_range_for_period("today")
        yesterday_start, yesterday_end = get_date_range_for_period("yesterday")
        this_week_start, _ = get_date_range_for_period("this_week")
        this_month_start, _ = get_date_range_for_period("this_month")

        # Today's metrics
        today_txs = db.query(Transaction).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.transaction_time >= today_start,
            Transaction.transaction_time <= today_end
        ).all()
        today_revenue = sum(t.amount for t in today_txs)
        today_count = len(today_txs)

        # Yesterday's metrics
        yesterday_txs = db.query(Transaction).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.transaction_time >= yesterday_start,
            Transaction.transaction_time <= yesterday_end
        ).all()
        yesterday_revenue = sum(t.amount for t in yesterday_txs)
        yesterday_count = len(yesterday_txs)

        # Revenue change percentage (Today vs Yesterday or This Week vs Last Week depending on dataset window)
        # If today has data, compare today vs yesterday. If zero, fallback to this week vs last week.
        if yesterday_revenue > 0:
            rev_change = calculate_percentage_change(yesterday_revenue, today_revenue)
        else:
            last_week_start, last_week_end = get_date_range_for_period("last_week")
            lw_txs = db.query(Transaction).filter(
                Transaction.merchant_id == merchant_id,
                Transaction.transaction_time >= last_week_start,
                Transaction.transaction_time <= last_week_end
            ).all()
            lw_rev = sum(t.amount for t in lw_txs)
            tw_txs = db.query(Transaction).filter(
                Transaction.merchant_id == merchant_id,
                Transaction.transaction_time >= this_week_start
            ).all()
            tw_rev = sum(t.amount for t in tw_txs)
            rev_change = calculate_percentage_change(lw_rev, tw_rev)

        # Weekly & Monthly Revenue
        weekly_txs = db.query(Transaction).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.transaction_time >= this_week_start
        ).all()
        weekly_revenue = sum(t.amount for t in weekly_txs)

        monthly_txs = db.query(Transaction).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.transaction_time >= this_month_start
        ).all()
        monthly_revenue = sum(t.amount for t in monthly_txs)

        # Average order value across all merchant transactions
        all_count = db.query(func.count(Transaction.id)).filter(Transaction.merchant_id == merchant_id).scalar() or 0
        all_sum = db.query(func.sum(Transaction.amount)).filter(Transaction.merchant_id == merchant_id).scalar() or 0.0
        aov = round(all_sum / all_count, 2) if all_count > 0 else 0.0

        # Customer counts
        new_cust = db.query(CustomerSegment).filter(
            CustomerSegment.merchant_id == merchant_id,
            CustomerSegment.segment == "new_customer"
        ).count()

        returning_cust = db.query(CustomerSegment).filter(
            CustomerSegment.merchant_id == merchant_id,
            CustomerSegment.segment.in_(["regular_customer", "loyal_customer", "high_value_customer"])
        ).count()

        inactive_cust = db.query(CustomerSegment).filter(
            CustomerSegment.merchant_id == merchant_id,
            CustomerSegment.segment == "inactive_regular"
        ).count()

        return AnalyticsOverview(
            merchant_id=merchant_id,
            today_revenue=round(today_revenue, 2),
            today_transactions=today_count,
            yesterday_revenue=round(yesterday_revenue, 2),
            yesterday_transactions=yesterday_count,
            revenue_change_percentage=rev_change,
            weekly_revenue=round(weekly_revenue, 2),
            monthly_revenue=round(monthly_revenue, 2),
            average_order_value=aov,
            new_customers_count=new_cust,
            returning_customers_count=returning_cust,
            inactive_regular_customers_count=inactive_cust
        )

    @staticmethod
    def get_hourly_analytics(db: Session, merchant_id: str, target_date: datetime = None) -> HourlyAnalytics:
        if target_date is None:
            target_date = datetime.utcnow()

        start_dt = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
        end_dt = start_dt + timedelta(days=1)

        # Query all transactions for that date or recent days if specific date has few transactions
        txs = db.query(Transaction).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.transaction_time >= start_dt,
            Transaction.transaction_time < end_dt
        ).all()

        # If zero txs today, analyze past 7 days to get average hourly breakdown
        if not txs:
            start_dt = datetime.utcnow() - timedelta(days=7)
            txs = db.query(Transaction).filter(
                Transaction.merchant_id == merchant_id,
                Transaction.transaction_time >= start_dt
            ).all()

        hourly_map = {h: {"revenue": 0.0, "count": 0} for h in range(24)}
        for t in txs:
            hour = t.transaction_time.hour
            hourly_map[hour]["revenue"] += t.amount
            hourly_map[hour]["count"] += 1

        buckets: List[HourlyBucket] = []
        for h in range(24):
            label = f"{h:02d}:00 - {(h+1)%24:02d}:00"
            buckets.append(HourlyBucket(
                hour=h,
                hour_label=label,
                revenue=round(hourly_map[h]["revenue"], 2),
                transaction_count=hourly_map[h]["count"]
            ))

        # Identify peak and slow hours (considering active business hours 08:00 - 22:00)
        business_hours = [b for b in buckets if 8 <= b.hour <= 22]
        business_hours_sorted = sorted(business_hours, key=lambda x: x.revenue, reverse=True)

        peak_hours = [b.hour_label for b in business_hours_sorted[:3] if b.revenue > 0]
        slow_hours = [b.hour_label for b in business_hours_sorted[-3:]]

        return HourlyAnalytics(
            merchant_id=merchant_id,
            date=start_dt.strftime("%Y-%m-%d"),
            hourly_data=buckets,
            peak_hours=peak_hours,
            slow_hours=slow_hours
        )

    @staticmethod
    def get_revenue_by_category(db: Session, merchant_id: str, period: str = "month") -> RevenueAnalytics:
        start_dt, end_dt = get_date_range_for_period("this_month" if period == "month" else "this_week")
        txs = db.query(Transaction).filter(
            Transaction.merchant_id == merchant_id,
            Transaction.transaction_time >= start_dt
        ).all()

        total_rev = sum(t.amount for t in txs)
        total_txs = len(txs)

        cat_map: Dict[str, Dict[str, float]] = {}
        for t in txs:
            cat = t.category or "general"
            if cat not in cat_map:
                cat_map[cat] = {"revenue": 0.0, "count": 0}
            cat_map[cat]["revenue"] += t.amount
            cat_map[cat]["count"] += 1

        categories: List[CategoryRevenue] = []
        for cat, data in cat_map.items():
            pct = round((data["revenue"] / total_rev * 100.0), 2) if total_rev > 0 else 0.0
            categories.append(CategoryRevenue(
                category=cat,
                revenue=round(data["revenue"], 2),
                transaction_count=int(data["count"]),
                percentage_of_total=pct
            ))

        categories.sort(key=lambda x: x.revenue, reverse=True)

        return RevenueAnalytics(
            merchant_id=merchant_id,
            period=period,
            total_revenue=round(total_rev, 2),
            total_transactions=total_txs,
            categories=categories
        )

    @staticmethod
    def get_customer_analytics(db: Session, merchant_id: str) -> CustomerAnalytics:
        total = db.query(Customer).filter(Customer.merchant_id == merchant_id).count()
        
        segments = db.query(CustomerSegment).filter(CustomerSegment.merchant_id == merchant_id).all()
        seg_counts = {
            "new_customer": 0,
            "regular_customer": 0,
            "loyal_customer": 0,
            "inactive_regular": 0,
            "high_value_customer": 0
        }
        for s in segments:
            if s.segment in seg_counts:
                seg_counts[s.segment] += 1

        return CustomerAnalytics(
            merchant_id=merchant_id,
            total_customers=total,
            new_customers=seg_counts["new_customer"],
            regular_customers=seg_counts["regular_customer"],
            loyal_customers=seg_counts["loyal_customer"],
            inactive_regular_customers=seg_counts["inactive_regular"],
            high_value_customers=seg_counts["high_value_customer"]
        )
