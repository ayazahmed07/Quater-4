import enum
from sqlalchemy import Column, Integer, Numeric, DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class InvoiceStatus(str, enum.Enum):
    GENERATED = "GENERATED"
    PARTIAL_PAID = "PARTIAL_PAID"
    PAID = "PAID"
    OVERDUE = "OVERDUE"


class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    ONLINE = "ONLINE"
    BANK_TRANSFER = "BANK_TRANSFER"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    billing_period_start = Column(DateTime, nullable=False)
    billing_period_end = Column(DateTime, nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    paid_amount = Column(Numeric(12, 2), nullable=False, default=0)
    balance_due = Column(Numeric(12, 2), nullable=False)
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.GENERATED, nullable=False)
    generated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    transaction_id = Column(Integer, ForeignKey("fueling_transactions.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)

    # Relationships
    invoice = relationship("Invoice", back_populates="items")
    transaction = relationship("FuelingTransaction", back_populates="invoice_items")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="RESTRICT"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    transaction_ref = Column(String(255), nullable=True)
    payment_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    recorded_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
    customer = relationship("Customer", back_populates="payments")
    recorded_by_user = relationship("User", foreign_keys=[recorded_by], back_populates="recorded_payments")
