from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class AnalyticsPeriodSummary(BaseModel):
    revenue: float
    transaction_count: int
    average_order_value: float


class AnalyticsOverview(BaseModel):
    merchant_id: str
    today_revenue: float
    today_transactions: int
    yesterday_revenue: float
    yesterday_transactions: int
    revenue_change_percentage: float
    weekly_revenue: float
    monthly_revenue: float
    average_order_value: float
    new_customers_count: int
    returning_customers_count: int
    inactive_regular_customers_count: int


class HourlyBucket(BaseModel):
    hour: int  # 0 to 23
    hour_label: str  # e.g., "16:00 - 17:00"
    revenue: float
    transaction_count: int


class HourlyAnalytics(BaseModel):
    merchant_id: str
    date: str
    hourly_data: List[HourlyBucket]
    peak_hours: List[str]
    slow_hours: List[str]


class CategoryRevenue(BaseModel):
    category: str
    revenue: float
    transaction_count: int
    percentage_of_total: float


class RevenueAnalytics(BaseModel):
    merchant_id: str
    period: str  # day, week, month
    total_revenue: float
    total_transactions: int
    categories: List[CategoryRevenue]


class CustomerAnalytics(BaseModel):
    merchant_id: str
    total_customers: int
    new_customers: int
    regular_customers: int
    loyal_customers: int
    inactive_regular_customers: int
    high_value_customers: int
