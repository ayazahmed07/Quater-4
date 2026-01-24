from pydantic import BaseModel, Field
from decimal import Decimal


class InventoryResponse(BaseModel):
    id: int
    product_id: int
    quantity: Decimal
    low_stock_threshold: Decimal

    class Config:
        from_attributes = True


class InventoryWithProduct(InventoryResponse):
    product_name: str
    product_type: str


class InventoryAdjust(BaseModel):
    quantity: Decimal  # Can be positive (add) or negative (remove)
    reason: str | None = None


class LowStockResponse(BaseModel):
    product_id: int
    product_name: str
    current_quantity: Decimal
    low_stock_threshold: Decimal
