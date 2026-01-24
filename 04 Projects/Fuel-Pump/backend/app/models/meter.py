from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class MeterReading(Base):
    __tablename__ = "meter_readings"

    id = Column(Integer, primary_key=True, index=True)
    pump_id = Column(String(50), nullable=False, default="1")  # Extensible for multiple pumps
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    opening_reading = Column(Numeric(10, 2), nullable=False)
    closing_reading = Column(Numeric(10, 2), nullable=True)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    recorded_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    # Relationships
    product = relationship("Product", back_populates="meter_readings")
    recorded_by_user = relationship("User", foreign_keys=[recorded_by], back_populates="meter_readings")
