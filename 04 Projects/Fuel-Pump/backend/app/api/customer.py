from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.api.deps import CurrentUser
from app.schemas.customer import CustomerResponse
from app.schemas.transaction import FuelingTransactionResponse, FuelingTransactionWithDetails
from app.schemas.invoice import InvoiceWithDetails
from app.models.user import User
from app.models.customer import Customer
from app.models.product import Product
from app.models.transaction import FuelingTransaction, TransactionStatus
from app.models.invoice import Invoice

router = APIRouter(prefix="/customer", tags=["Customer"])


async def get_current_customer(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> Customer:
    result = await db.execute(select(Customer).where(Customer.user_id == current_user.id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found",
        )
    return customer


CurrentCustomer = Annotated[Customer, Depends(get_current_customer)]


@router.get("/profile", response_model=CustomerResponse)
async def get_profile(customer: CurrentCustomer):
    return CustomerResponse.model_validate(customer)


@router.put("/profile", response_model=CustomerResponse)
async def update_profile(
    profile_data: dict,
    customer: CurrentCustomer,
    db: AsyncSession = Depends(get_db),
):
    for field, value in profile_data.items():
        if hasattr(customer, field):
            setattr(customer, field, value)
    await db.commit()
    await db.refresh(customer)
    return CustomerResponse.model_validate(customer)


@router.get("/statements", response_model=list[FuelingTransactionWithDetails])
async def get_statements(
    customer: CurrentCustomer,
    db: AsyncSession = Depends(get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    query = (
        select(FuelingTransaction, Product)
        .join(Product, FuelingTransaction.product_id == Product.id)
        .where(
            FuelingTransaction.customer_id == customer.id,
            FuelingTransaction.status == TransactionStatus.POSTED
        )
    )
    if start_date:
        query = query.where(FuelingTransaction.transaction_date >= start_date)
    if end_date:
        query = query.where(FuelingTransaction.transaction_date <= end_date)
    result = await db.execute(query.order_by(FuelingTransaction.transaction_date.desc()))
    rows = result.all()
    return [
        FuelingTransactionWithDetails(
            **FuelingTransactionResponse.model_validate(t).model_dump(),
            customer_name=customer.name,
            product_name=p.name,
            creator_name=str(t.created_by),
            confirmer_name=str(t.confirmed_by) if t.confirmed_by else None,
        )
        for t, p in rows
    ]


@router.get("/invoices", response_model=list[InvoiceWithDetails])
async def get_invoices(
    customer: CurrentCustomer,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Invoice)
        .where(Invoice.customer_id == customer.id)
        .order_by(Invoice.generated_at.desc())
    )
    invoices = result.scalars().all()
    return [
        InvoiceWithDetails(
            **InvoiceWithDetails.model_validate(i).model_dump(),
            customer_name=customer.name,
        )
        for i in invoices
    ]


@router.get("/invoices/{invoice_id}", response_model=InvoiceWithDetails)
async def get_invoice(
    invoice_id: int,
    customer: CurrentCustomer,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Invoice).where(
            and_(
                Invoice.id == invoice_id,
                Invoice.customer_id == customer.id
            )
        )
    )
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return InvoiceWithDetails(
        **InvoiceWithDetails.model_validate(invoice).model_dump(),
        customer_name=customer.name,
    )
