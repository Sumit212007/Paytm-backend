import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, Date, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from app.database.connection import Base


def generate_uuid():
    return str(uuid.uuid4())


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    business_name = Column(String(255), nullable=False)
    business_type = Column(String(100), nullable=False)
    location = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    language_preference = Column(String(50), default="hinglish")  # english, hindi, hinglish
    timezone = Column(String(50), default="Asia/Kolkata")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customers = relationship("Customer", back_populates="merchant", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="merchant", cascade="all, delete-orphan")
    segments = relationship("CustomerSegment", back_populates="merchant", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="merchant", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="merchant", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="merchant", cascade="all, delete-orphan")
    notifications = relationship("MerchantNotification", back_populates="merchant", cascade="all, delete-orphan")
    ai_conversations = relationship("AIConversation", back_populates="merchant", cascade="all, delete-orphan")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, default=generate_uuid)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False, index=True)
    customer_reference = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    first_purchase_at = Column(DateTime, nullable=True)
    last_purchase_at = Column(DateTime, nullable=True)
    total_transactions = Column(Integer, default=0)
    total_spend = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    merchant = relationship("Merchant", back_populates="customers")
    transactions = relationship("Transaction", back_populates="customer")
    segments = relationship("CustomerSegment", back_populates="customer", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=generate_uuid)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False, index=True)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=True, index=True)
    amount = Column(Float, nullable=False)
    transaction_time = Column(DateTime, nullable=False, index=True)
    payment_method = Column(String(50), default="paytm_qr")  # paytm_qr, upi, card, cash
    category = Column(String(100), default="general")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    merchant = relationship("Merchant", back_populates="transactions")
    customer = relationship("Customer", back_populates="transactions")


class CustomerSegment(Base):
    __tablename__ = "customer_segments"

    id = Column(String, primary_key=True, default=generate_uuid)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False, index=True)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False, index=True)
    segment = Column(String(100), nullable=False)  # new_customer, regular_customer, loyal_customer, inactive_regular, high_value_customer
    score = Column(Float, default=1.0)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    merchant = relationship("Merchant", back_populates="segments")
    customer = relationship("Customer", back_populates="segments")


class BusinessMetric(Base):
    __tablename__ = "business_metrics"

    id = Column(String, primary_key=True, default=generate_uuid)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False, index=True)
    metric_date = Column(Date, nullable=False, index=True)
    revenue = Column(Float, default=0.0)
    transaction_count = Column(Integer, default=0)
    average_order_value = Column(Float, default=0.0)
    new_customers = Column(Integer, default=0)
    returning_customers = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Insight(Base):
    __tablename__ = "insights"

    id = Column(String, primary_key=True, default=generate_uuid)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False, index=True)
    type = Column(String(100), nullable=False)  # sales_drop, slow_hours, customer_inactivity, revenue_growth, customer_growth, campaign_result
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    severity = Column(String(50), default="medium")  # low, medium, high, critical
    data = Column(JSON, nullable=True)
    status = Column(String(50), default="active")  # active, dismissed, resolved, expired
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    merchant = relationship("Merchant", back_populates="insights")
    recommendations = relationship("Recommendation", back_populates="insight", cascade="all, delete-orphan")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String, primary_key=True, default=generate_uuid)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False, index=True)
    insight_id = Column(String, ForeignKey("insights.id"), nullable=True, index=True)
    type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    target_segment = Column(String(100), nullable=False)
    offer_type = Column(String(100), nullable=False)  # flat_discount, percentage_discount, cashback, free_item
    offer_value = Column(Float, nullable=False)
    minimum_order_value = Column(Float, default=0.0)
    recommended_time_start = Column(String(20), nullable=True)  # e.g., "16:00"
    recommended_time_end = Column(String(20), nullable=True)    # e.g., "19:00"
    duration_days = Column(Integer, default=3)
    estimated_revenue = Column(Float, default=0.0)
    reason = Column(Text, nullable=True)
    ai_generated = Column(Boolean, default=True)
    status = Column(String(50), default="pending")  # pending, approved, rejected, expired, executed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    merchant = relationship("Merchant", back_populates="recommendations")
    insight = relationship("Insight", back_populates="recommendations")
    campaigns = relationship("Campaign", back_populates="recommendation")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String, primary_key=True, default=generate_uuid)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False, index=True)
    recommendation_id = Column(String, ForeignKey("recommendations.id"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    campaign_type = Column(String(100), nullable=False)
    target_segment = Column(String(100), nullable=False)
    offer_type = Column(String(100), nullable=False)
    offer_value = Column(Float, nullable=False)
    minimum_order_value = Column(Float, default=0.0)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration_days = Column(Integer, default=3)
    status = Column(String(50), default="draft")  # draft, pending_approval, approved, running, completed, cancelled
    approved_at = Column(DateTime, nullable=True)
    launched_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    merchant = relationship("Merchant", back_populates="campaigns")
    recommendation = relationship("Recommendation", back_populates="campaigns")
    targets = relationship("CampaignTarget", back_populates="campaign", cascade="all, delete-orphan")
    result = relationship("CampaignResult", back_populates="campaign", uselist=False, cascade="all, delete-orphan")


class CampaignTarget(Base):
    __tablename__ = "campaign_targets"

    id = Column(String, primary_key=True, default=generate_uuid)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False, index=True)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False, index=True)
    eligible = Column(Boolean, default=True)
    notification_status = Column(String(50), default="pending")  # pending, sent, delivered, failed
    redeemed = Column(Boolean, default=False)
    redeemed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    campaign = relationship("Campaign", back_populates="targets")
    customer = relationship("Customer")


class MerchantNotification(Base):
    __tablename__ = "merchant_notifications"

    id = Column(String, primary_key=True, default=generate_uuid)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False, index=True)
    type = Column(String(100), nullable=False)  # new_insight, campaign_result, new_recommendation, weekly_summary
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    related_insight_id = Column(String, nullable=True)
    related_campaign_id = Column(String, nullable=True)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    merchant = relationship("Merchant", back_populates="notifications")


class CustomerNotification(Base):
    __tablename__ = "customer_notifications"

    id = Column(String, primary_key=True, default=generate_uuid)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False, index=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(50), default="sent")  # sent, delivered, read
    sent_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CampaignResult(Base):
    __tablename__ = "campaign_results"

    id = Column(String, primary_key=True, default=generate_uuid)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False, index=True, unique=True)
    targeted_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    opened_count = Column(Integer, default=0)
    redeemed_count = Column(Integer, default=0)
    revenue_generated = Column(Float, default=0.0)
    revenue_lift_percentage = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    campaign = relationship("Campaign", back_populates="result")


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(String, primary_key=True, default=generate_uuid)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # user, assistant
    message = Column(Text, nullable=False)
    language = Column(String(50), default="hinglish")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    merchant = relationship("Merchant", back_populates="ai_conversations")
