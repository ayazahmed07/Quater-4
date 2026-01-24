from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from app.models.invoice import InvoiceStatus, PaymentMethod


class InvoiceItemResponse(BaseModel):
    id: int
    transaction_id: int
    quantity: Decimal
    unit_price: Decimal
    total_amount: Decimal

    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    id: int
    customer_id: int
    invoice_number: str
    billing_period_start: datetime
    billing_period_end: datetime
    total_amount: Decimal
    paid_amount: Decimal
    balance_due: Decimal
    status: InvoiceStatus
    generated_at: datetime
    due_date: datetime

    class Config:
        from_attributes = True


class InvoiceWithDetails(InvoiceResponse):
    customer_name: str
    items: list[InvoiceItemResponse] = []


class PaymentCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)
    payment_method: PaymentMethod
    transaction_ref: str | None = None
    notes: str | None = None


class PaymentResponse(BaseModel):
    id: int
    invoice_id: int
    customer_id: int
    amount: Decimal
    payment_method: PaymentMethod
    transaction_ref: str | None
    payment_date: datetime
    notes: str | None

    class Config:
        from_attributes = True
