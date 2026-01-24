from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal


class MeterReadingCreate(BaseModel):
    product_id: int
    opening_reading: Decimal = Field(..., ge=0)
    closing_reading: Decimal | None = None


class MeterReadingResponse(BaseModel):
    id: int
    pump_id: str
    product_id: int
    opening_reading: Decimal
    closing_reading: Decimal | None
    date: datetime
    recorded_by: int

    class Config:
        from_attributes = True


class MeterReadingWithDetails(MeterReadingResponse):
    product_name: str
    recorded_by_name: str


class ReconciliationResult(BaseModel):
    is_matched: bool
    system_total: Decimal
    actual_meter_total: Decimal
    difference: Decimal
