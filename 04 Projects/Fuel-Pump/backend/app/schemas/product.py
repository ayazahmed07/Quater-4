from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from app.models.product import ProductType, FuelType, ProductUnit


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: ProductType
    fuel_type: FuelType | None = None
    current_price: Decimal = Field(..., gt=0)
    unit: ProductUnit


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    current_price: Decimal | None = None
    low_stock_threshold: Decimal | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    type: ProductType
    fuel_type: FuelType | None
    current_price: Decimal
    unit: ProductUnit
    created_at: datetime

    class Config:
        from_attributes = True


class ProductWithInventory(ProductResponse):
    quantity: Decimal | None = None
    low_stock_threshold: Decimal | None = None


class PriceUpdate(BaseModel):
    new_price: Decimal = Field(..., gt=0)


class PriceHistoryResponse(BaseModel):
    id: int
    product_id: int
    price: Decimal
    effective_from: datetime
    effective_to: datetime | None

    class Config:
        from_attributes = True
