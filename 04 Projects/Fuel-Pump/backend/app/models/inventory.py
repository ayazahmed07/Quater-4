from sqlalchemy import Column, Integer, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), unique=True, nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False, default=0)
    low_stock_threshold = Column(Numeric(10, 2), nullable=False, default=10)

    # Relationships
    product = relationship("Product", back_populates="inventory")
