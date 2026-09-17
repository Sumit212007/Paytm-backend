from typing import Optional, List
from sqlalchemy.orm import Session
from app.database.models import Customer, CustomerSegment
from app.schemas.customer import CustomerCreate


class CustomerService:
    @staticmethod
    def get_customer(db: Session, customer_id: str) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.id == customer_id).first()

    @staticmethod
    def get_merchant_customers(db: Session, merchant_id: str) -> List[Customer]:
        return db.query(Customer).filter(Customer.merchant_id == merchant_id).all()

    @staticmethod
    def get_merchant_segments(db: Session, merchant_id: str) -> List[CustomerSegment]:
        return db.query(CustomerSegment).filter(CustomerSegment.merchant_id == merchant_id).all()

    @staticmethod
    def create_customer(db: Session, data: CustomerCreate) -> Customer:
        customer = Customer(
            merchant_id=data.merchant_id,
            customer_reference=data.customer_reference,
            name=data.name,
            phone=data.phone
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer
