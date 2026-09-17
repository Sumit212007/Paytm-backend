import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.connection import Base
from app.database.models import Merchant, Customer, Transaction, Insight, Recommendation, Campaign
from datetime import datetime, timedelta


@pytest.fixture(scope="function")
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Create test merchant
    merchant = Merchant(
        id="test_mer_001",
        name="Test Merchant",
        business_name="Test Store",
        business_type="Grocery",
        location="Delhi",
        phone="+919999999999",
        language_preference="hinglish"
    )
    session.add(merchant)
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)
