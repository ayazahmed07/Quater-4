from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from app.models.transaction import TransactionMode, TransactionStatus, PaymentType


class FuelingTransactionBase(BaseModel):
    product_id: int
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal
    total_amount: Decimal
    mode: TransactionMode
    payment_type: PaymentType
    cash_amount: Decimal = Field(default=Decimal("0"), ge=0)
    credit_amount: Decimal = Field(default=Decimal("0"), ge=0)
    customer_id: int | None = None  # None = cash customer
    meter_reading: Decimal | None = None


class FuelingTransactionCreate(BaseModel):
    product_id: int
    quantity: Decimal | None = None  # For liter-based
    amount: Decimal | None = None  # For amount-based
    mode: TransactionMode
    customer_id: int | None = None
    payment_type: PaymentType = PaymentType.CASH
    cash_amount: Decimal = Field(default=Decimal("0"), ge=0)
    credit_amount: Decimal = Field(default=Decimal("0"), ge=0)
    meter_reading: Decimal | None = None


class FuelingTransactionResponse(BaseModel):
    id: int
    customer_id: int | None
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    total_amount: Decimal
    mode: TransactionMode
    status: TransactionStatus
    payment_type: PaymentType
    cash_amount: Decimal
    credit_amount: Decimal
    transaction_date: datetime
    meter_reading: Decimal | None
    created_by: int
    confirmed_by: int | None
    confirmed_at: datetime | None
    rejection_reason: str | None

    class Config:
        from_attributes = True


class FuelingTransactionWithDetails(FuelingTransactionResponse):
    customer_name: str | None = None
    product_name: str
    creator_name: str
    confirmer_name: str | None = None


class TransactionConfirm(BaseModel):
    pass


class TransactionReject(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)
