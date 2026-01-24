from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.database import get_db
from app.api.deps import CurrentUser, RequireAdmin
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerWithUser, CustomerUpdate
from app.schemas.product import ProductCreate, ProductResponse, ProductWithInventory, ProductUpdate, PriceUpdate, PriceHistoryResponse
from app.schemas.transaction import FuelingTransactionResponse, FuelingTransactionWithDetails, TransactionConfirm, TransactionReject
from app.schemas.invoice import InvoiceWithDetails
from app.models.user import User
from app.models.customer import Customer
from app.models.product import Product, PriceHistory
from app.models.inventory import Inventory
from app.models.transaction import FuelingTransaction, TransactionStatus
from app.models.invoice import Invoice, InvoiceStatus
from app.core.security import get_password_hash

router = APIRouter(prefix="/admin", tags=["Admin"])


# ==================== User Management ====================
@router.get("/users", response_model=list[UserResponse])
async def list_users(
    current_user: RequireAdmin,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [UserResponse.model_validate(u) for u in users]


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: RequireAdmin,
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(User).where(User.email == user_data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: RequireAdmin,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


# ==================== Customer Management ====================
@router.get("/customers", response_model=list[CustomerWithUser])
async def list_customers(
    current_user: RequireAdmin,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Customer, User).join(User, Customer.user_id == User.id)
    )
    rows = result.all()
    return [
        CustomerWithUser(
            **CustomerResponse.model_validate(c).model_dump(),
            email=u.email
        )
        for c, u in rows
    ]


@router.post("/customers", response_model=CustomerWithUser, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    current_user: RequireAdmin,
    db: AsyncSession = Depends(get_db),
):
    existing_user = await db.execute(select(User).where(User.email == customer_data.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = User(
        email=customer_data.email,
        password_hash=get_password_hash(customer_data.password),
        role=customer_data.role,
    )
    db.add(user)
    await db.flush()
    customer = Customer(
        user_id=user.id,
        name=customer_data.name,
        phone=customer_data.phone,
        address=customer_data.address,
        credit_limit=customer_data.credit_limit,
        status=customer_data.status,
    )
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return CustomerWithUser(
        **CustomerResponse.model_validate(customer).model_dump(),
        email=user.email
    )


@router.put("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    current_user: RequireAdmin,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )
    for field, value in customer_data.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    await db.commit()
    await db.refresh(customer)
    return CustomerResponse.model_validate(customer)


# ==================== Product Management ====================
@router.get("/products", response_model=list[ProductWithInventory])
async def list_products(
    current_user: RequireAdmin,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Product, Inventory)
        .outerjoin(Inventory, Product.id == Inventory.product_id)
    )
    rows = result.all()
    return [
        ProductWithInventory(
            **ProductResponse.model_validate(p).model_dump(),
            quantity=i.quantity if i else None,
            low_stock_threshold=i.low_stock_threshold if i else None,
        )
        for p, i in rows
    ]


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    current_user: RequireAdmin,
    db: AsyncSession = Depends(get_db),
):
    product = Product(**product_data.model_dump())
    db.add(product)
    await db.flush()
    # Create inventory record
    inventory = Inventory(
        product_id=product.id,
        quantity=Decimal("0"),
        low_stock_threshold=Decimal("10"),
    )
    db.add(inventory)
    await db.commit()
    await db.refresh(product)
    return ProductResponse.model_validate(product)


@router.put("/products/{product_id}/update-price", response_model=ProductResponse)
async def update_product_price(
    product_id: int,
    price_data: PriceUpdate,
    current_user: RequireAdmin,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    # Archive current price
    old_price = PriceHistory(
        product_id=product.id,
        price=product.current_price,
        effective_from=product.created_at,
        effective_to=datetime.utcnow(),
    )
    db.add(old_price)
    # Update price
    product.current_price = price_data.new_price
    await db.commit()
    await db.refresh(product)
    return ProductResponse.model_validate(product)


@router.get("/products/{product_id}/price-history", response_model=list[PriceHistoryResponse])
async def get_price_history(
    product_id: int,
    current_user: RequireAdmin,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PriceHistory)
        .where(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.effective_from.desc())
    )
    history = result.scalars().all()
    return [PriceHistoryResponse.model_validate(h) for h in history]


# ==================== Transaction Management ====================
@router.get("/transactions/pending", response_model=list[FuelingTransactionWithDetails])
async def list_pending_transactions(
    current_user: RequireAdmin,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FuelingTransaction, Product, User, Customer)
        .join(Product, FuelingTransaction.product_id == Product.id)
        .join(User, FuelingTransaction.created_by == User.id)
        .outerjoin(Customer, FuelingTransaction.customer_id == Customer.id)
        .where(FuelingTransaction.status == TransactionStatus.PENDING)
        .order_by(FuelingTransaction.transaction_date.desc())
    )
    rows = result.all()
    return [
        FuelingTransactionWithDetails(
            **FuelingTransactionResponse.model_validate(t).model_dump(),
            customer_name=c.name if c else None,
            product_name=p.name,
            creator_name=u.email,
            confirmer_name=None,
        )
        for t, p, u, c in rows
    ]


@router.put("/transactions/{transaction_id}/confirm", response_model=FuelingTransactionResponse)
async def confirm_transaction(
    transaction_id: int,
    current_user: RequireAdmin,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FuelingTransaction).where(FuelingTransaction.id == transaction_id)
    )
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    if transaction.status != TransactionStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction is not in pending status",
        )
    transaction.status = TransactionStatus.POSTED
    transaction.confirmed_by = current_user.id
    transaction.confirmed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(transaction)
    return FuelingTransactionResponse.model_validate(transaction)


@router.put("/transactions/{transaction_id}/reject", response_model=FuelingTransactionResponse)
async def reject_transaction(
    transaction_id: int,
    reject_data: TransactionReject,
    current_user: RequireAdmin,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FuelingTransaction).where(FuelingTransaction.id == transaction_id)
    )
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    if transaction.status != TransactionStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction is not in pending status",
        )
    transaction.status = TransactionStatus.REJECTED
    transaction.confirmed_by = current_user.id
    transaction.confirmed_at = datetime.utcnow()
    transaction.rejection_reason = reject_data.reason
    await db.commit()
    await db.refresh(transaction)
    return FuelingTransactionResponse.model_validate(transaction)


# ==================== Invoice Management ====================
@router.get("/invoices", response_model=list[InvoiceWithDetails])
async def list_invoices(
    current_user: RequireAdmin,
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[InvoiceStatus] = None,
):
    query = (
        select(Invoice, Customer)
        .join(Customer, Invoice.customer_id == Customer.id)
    )
    if status_filter:
        query = query.where(Invoice.status == status_filter)
    result = await db.execute(query.order_by(Invoice.generated_at.desc()))
    rows = result.all()
    return [
        InvoiceWithDetails(
            **InvoiceWithDetails.model_validate(i).model_dump(),
            customer_name=c.name,
        )
        for i, c in rows
    ]


@router.post("/invoices/generate", status_code=status.HTTP_201_CREATED)
async def generate_invoices(
    current_user: RequireAdmin,
    db: AsyncSession = Depends(get_db),
):
    # This will be implemented in the billing service
    # For now, return a placeholder
    return {"message": "Invoice generation will be implemented in billing service"}
