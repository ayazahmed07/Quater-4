from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.core.rbac import Role


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(Role), nullable=False, default=Role.CUSTOMER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="user", uselist=False)
    created_transactions = relationship("FuelingTransaction", foreign_keys="FuelingTransaction.created_by", back_populates="creator")
    confirmed_transactions = relationship("FuelingTransaction", foreign_keys="FuelingTransaction.confirmed_by", back_populates="confirmer")
    recorded_payments = relationship("Payment", back_populates="recorded_by_user")
    meter_readings = relationship("MeterReading", back_populates="recorded_by_user")
