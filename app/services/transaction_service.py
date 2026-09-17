from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.models import Transaction, Customer
from app.schemas.transaction import TransactionCreate


class TransactionService:
    @staticmethod
    def get_merchant_transactions(
        db: Session,
        merchant_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Transaction]:
        return db.query(Transaction).filter(
            Transaction.merchant_id == merchant_id
        ).order_by(Transaction.transaction_time.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def create_transaction(db: Session, data: TransactionCreate) -> Transaction:
        tx = Transaction(
            merchant_id=data.merchant_id,
            customer_id=data.customer_id,
            amount=data.amount,
            transaction_time=data.transaction_time or datetime.utcnow(),
            payment_method=data.payment_method,
            category=data.category
        )
        db.add(tx)

        # Update customer stats if customer_id is provided
        if data.customer_id:
            cust = db.query(Customer).filter(Customer.id == data.customer_id).first()
            if cust:
                cust.total_transactions += 1
                cust.total_spend += data.amount
                cust.last_purchase_at = tx.transaction_time
                if not cust.first_purchase_at:
                    cust.first_purchase_at = tx.transaction_time

        db.commit()
        db.refresh(tx)
        return tx
