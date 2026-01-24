from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from decimal import Decimal
from app.database import get_db
from app.api.deps import CurrentUser
from app.schemas.transaction import FuelingTransactionCreate, FuelingTransactionResponse, FuelingTransactionWithDetails
from app.schemas.meter import MeterReadingCreate, MeterReadingResponse, MeterReadingWithDetails
from app.models.transaction import FuelingTransaction, TransactionMode, PaymentType, TransactionStatus
from app.models.product import Product
from app.models.customer import Customer
from app.models.user import User
from app.models.meter import MeterReading

router = APIRouter(prefix="/cashier", tags=["Cashier"])


@router.post("/transactions", response_model=FuelingTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_fueling_transaction(
    transaction_data: FuelingTransactionCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    # Get product
    product_result = await db.execute(select(Product).where(Product.id == transaction_data.product_id))
    product = product_result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # Calculate quantity and amount based on mode
    quantity: Decimal
    unit_price: Decimal = product.current_price
    total_amount: Decimal

    if transaction_data.mode == TransactionMode.LITER_BASED:
        if transaction_data.quantity is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity required for liter-based mode",
            )
        quantity = transaction_data.quantity
        total_amount = quantity * unit_price
    else:  # AMOUNT_BASED
        if transaction_data.amount is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount required for amount-based mode",
            )
        total_amount = transaction_data.amount
        quantity = total_amount / unit_price if unit_price > 0 else Decimal("0")

    # Validate payment amounts
    if transaction_data.payment_type == PaymentType.MIXED:
        if transaction_data.cash_amount + transaction_data.credit_amount != total_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cash + Credit amount must equal total amount ({total_amount})",
            )
        cash_amount = transaction_data.cash_amount
        credit_amount = transaction_data.credit_amount
    elif transaction_data.payment_type == PaymentType.CASH:
        cash_amount = total_amount
        credit_amount = Decimal("0")
    else:  # CREDIT
        if transaction_data.customer_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer required for credit payment",
            )
        cash_amount = Decimal("0")
        credit_amount = total_amount

    # Verify customer exists if provided
    if transaction_data.customer_id:
        customer_result = await db.execute(
            select(Customer).where(Customer.id == transaction_data.customer_id)
        )
        customer = customer_result.scalar_one_or_none()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found",
            )

    # Create transaction
    transaction = FuelingTransaction(
        customer_id=transaction_data.customer_id,
        product_id=product.id,
        quantity=quantity,
        unit_price=unit_price,
        total_amount=total_amount,
        mode=transaction_data.mode,
        payment_type=transaction_data.payment_type,
        cash_amount=cash_amount,
        credit_amount=credit_amount,
        meter_reading=transaction_data.meter_reading,
        created_by=current_user.id,
        status=TransactionStatus.PENDING,
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return FuelingTransactionResponse.model_validate(transaction)


@router.get("/transactions/my-pending", response_model=list[FuelingTransactionWithDetails])
async def get_my_pending_transactions(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FuelingTransaction, Product, Customer)
        .join(Product, FuelingTransaction.product_id == Product.id)
        .outerjoin(Customer, FuelingTransaction.customer_id == Customer.id)
        .where(
            FuelingTransaction.created_by == current_user.id,
            FuelingTransaction.status == TransactionStatus.PENDING
        )
        .order_by(FuelingTransaction.transaction_date.desc())
    )
    rows = result.all()
    return [
        FuelingTransactionWithDetails(
            **FuelingTransactionResponse.model_validate(t).model_dump(),
            customer_name=c.name if c else None,
            product_name=p.name,
            creator_name=current_user.email,
            confirmer_name=None,
        )
        for t, p, c in rows
    ]


@router.post("/meter-readings", response_model=MeterReadingResponse, status_code=status.HTTP_201_CREATED)
async def create_meter_reading(
    reading_data: MeterReadingCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    # Verify product exists
    product_result = await db.execute(select(Product).where(Product.id == reading_data.product_id))
    product = product_result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # Check if there's an unclosed reading for today
    from sqlalchemy import and_
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    existing_result = await db.execute(
        select(MeterReading).where(
            and_(
                MeterReading.product_id == reading_data.product_id,
                MeterReading.date >= today_start,
                MeterReading.closing_reading.is_(None)
            )
        )
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There's an unclosed meter reading for this product today. Please close it first.",
        )

    meter_reading = MeterReading(
        product_id=reading_data.product_id,
        opening_reading=reading_data.opening_reading,
        recorded_by=current_user.id,
    )
    db.add(meter_reading)
    await db.commit()
    await db.refresh(meter_reading)
    return MeterReadingResponse.model_validate(meter_reading)


@router.put("/meter-readings/{reading_id}/close", response_model=MeterReadingResponse)
async def close_meter_reading(
    reading_id: int,
    current_user: CurrentUser,
    closing_reading: Decimal = Query(..., description="Closing meter reading value"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(MeterReading).where(MeterReading.id == reading_id))
    meter_reading = result.scalar_one_or_none()
    if not meter_reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meter reading not found",
        )
    if meter_reading.closing_reading is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meter reading already closed",
        )

    # Reconcile with system total
    from sqlalchemy import and_
    system_result = await db.execute(
        select(func.sum(FuelingTransaction.quantity))
        .where(
            and_(
                FuelingTransaction.product_id == meter_reading.product_id,
                FuelingTransaction.status == TransactionStatus.POSTED,
                FuelingTransaction.transaction_date >= meter_reading.date
            )
        )
    )
    system_total = system_result.scalar() or Decimal("0")
    expected_reading = meter_reading.opening_reading + system_total

    if closing_reading != expected_reading:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Meter mismatch. Expected: {expected_reading}, Got: {closing_reading}",
        )

    meter_reading.closing_reading = closing_reading
    await db.commit()
    await db.refresh(meter_reading)
    return MeterReadingResponse.model_validate(meter_reading)


@router.get("/meter-readings", response_model=list[MeterReadingWithDetails])
async def get_meter_readings(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
):
    result = await db.execute(
        select(MeterReading, Product)
        .join(Product, MeterReading.product_id == Product.id)
        .order_by(MeterReading.date.desc())
        .limit(limit)
    )
    rows = result.all()
    return [
        MeterReadingWithDetails(
            **MeterReadingResponse.model_validate(m).model_dump(),
            product_name=p.name,
            recorded_by_name=current_user.email,
        )
        for m, p in rows
    ]
