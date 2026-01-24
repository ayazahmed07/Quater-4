from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from app.models.customer import CustomerStatus


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=10, max_length=20)
    address: str | None = None
    credit_limit: Decimal = Field(default=Decimal("0"), ge=0)
    status: CustomerStatus = CustomerStatus.ACTIVE


class CustomerCreate(CustomerBase):
    email: str  # For user account
    password: str = Field(..., min_length=6)  # Temporary password


class CustomerUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    address: str | None = None
    credit_limit: Decimal | None = None
    status: CustomerStatus | None = None


class CustomerResponse(BaseModel):
    id: int
    user_id: int
    name: str
    phone: str
    address: str | None
    credit_limit: Decimal
    status: CustomerStatus
    created_at: datetime

    class Config:
        from_attributes = True


class CustomerWithUser(CustomerResponse):
    email: str  # User email
