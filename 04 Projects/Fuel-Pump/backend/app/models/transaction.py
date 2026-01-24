import enum
from sqlalchemy import Column, Integer, Numeric, DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class TransactionMode(str, enum.Enum):
    LITER_BASED = "LITER_BASED"
    AMOUNT_BASED = "AMOUNT_BASED"


class TransactionStatus(str, enum.Enum):
    PENDING = "PENDING"
    POSTED = "POSTED"
    REJECTED = "REJECTED"


class PaymentType(str, enum.Enum):
    CASH = "CASH"
    CREDIT = "CREDIT"
    MIXED = "MIXED"


class FuelingTransaction(Base):
    __tablename__ = "fueling_transactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)  # NULL = cash customer
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    mode = Column(SQLEnum(TransactionMode), nullable=False)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    payment_type = Column(SQLEnum(PaymentType), nullable=False)
    cash_amount = Column(Numeric(12, 2), nullable=False, default=0)
    credit_amount = Column(Numeric(12, 2), nullable=False, default=0)
    transaction_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    meter_reading = Column(Numeric(10, 2), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    confirmed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="transactions")
    product = relationship("Product", back_populates="transactions")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_transactions")
    confirmer = relationship("User", foreign_keys=[confirmed_by], back_populates="confirmed_transactions")
    invoice_items = relationship("InvoiceItem", back_populates="transaction")
