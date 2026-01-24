import enum
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ProductType(str, enum.Enum):
    FUEL = "FUEL"
    LUBRICANT = "LUBRICANT"


class FuelType(str, enum.Enum):
    PETROL = "PETROL"
    HSD = "HSD"
    HOBC = "HOBC"


class ProductUnit(str, enum.Enum):
    LITER = "LITER"
    UNIT = "UNIT"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(SQLEnum(ProductType), nullable=False)
    fuel_type = Column(SQLEnum(FuelType), nullable=True)  # Only for FUEL products
    current_price = Column(Numeric(10, 2), nullable=False)
    unit = Column(SQLEnum(ProductUnit), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan")
    transactions = relationship("FuelingTransaction", back_populates="product")
    meter_readings = relationship("MeterReading", back_populates="product")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    effective_from = Column(DateTime, nullable=False, default=datetime.utcnow)
    effective_to = Column(DateTime, nullable=True)

    # Relationships
    product = relationship("Product", back_populates="price_history")
