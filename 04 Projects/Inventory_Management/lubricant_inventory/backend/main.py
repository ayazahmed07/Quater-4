"""
MAIN.PY - FastAPI Application
==============================
Main API application with all routes.
"""

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
import pandas as pd
import sqlite3
import io

from database import init_db, create_default_users, DB_PATH
from auth import authenticate_user, create_access_token, verify_token, get_user_by_id
from models import *
from crud import *
from reports import *

# Initialize FastAPI app
app = FastAPI(title="Lubricant Inventory API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()


# ==================== STARTUP EVENTS ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    create_default_users()


# ==================== AUTH DEPENDENCY ====================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get the current authenticated user from JWT token."""
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    user = get_user_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


# ==================== AUTH ROUTES ====================

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(login_request: LoginRequest):
    """Authenticate user and return JWT token."""
    user = authenticate_user(login_request.username, login_request.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(data={"sub": str(user["user_id"]), "username": user["username"]})

    return TokenResponse(
        access_token=access_token,
        user=UserResponse(**user)
    )


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user."""
    return UserResponse(**current_user)


# ==================== DASHBOARD ====================

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats_endpoint(current_user: dict = Depends(get_current_user)):
    """Get dashboard statistics."""
    stats = get_dashboard_stats()
    return DashboardStats(**stats)


# ==================== ITEMS ====================

@app.get("/api/items", response_model=List[ItemResponse])
async def get_items_endpoint(current_user: dict = Depends(get_current_user)):
    """Get all items."""
    items = get_all_items()
    return [ItemResponse(**item) for item in items]


@app.get("/api/items/{item_id}", response_model=ItemResponse)
async def get_item_endpoint(item_id: int, current_user: dict = Depends(get_current_user)):
    """Get an item by ID."""
    item = get_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemResponse(**item)


@app.post("/api/items", response_model=ItemResponse)
async def create_item_endpoint(item: ItemCreate, current_user: dict = Depends(get_current_user)):
    """Create a new item."""
    item_id = create_item(
        item_name=item.item_name,
        grade=item.grade,
        pack_size=item.pack_size,
        purchase_price=item.purchase_price,
        sale_price=item.sale_price,
        opening_stock=item.opening_stock
    )
    created_item = get_item_by_id(item_id)
    return ItemResponse(**created_item)


@app.put("/api/items/{item_id}", response_model=ItemResponse)
async def update_item_endpoint(item_id: int, item: ItemUpdate, current_user: dict = Depends(get_current_user)):
    """Update an item."""
    success = update_item(
        item_id=item_id,
        item_name=item.item_name,
        grade=item.grade,
        pack_size=item.pack_size,
        purchase_price=item.purchase_price,
        sale_price=item.sale_price
    )
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    updated_item = get_item_by_id(item_id)
    return ItemResponse(**updated_item)


@app.delete("/api/items/{item_id}")
async def delete_item_endpoint(item_id: int, current_user: dict = Depends(get_current_user)):
    """Delete an item."""
    success = delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}


@app.post("/api/items/import")
async def import_items_endpoint(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Import items from Excel file."""
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))

        count = import_items_from_excel(df)
        return {"message": f"Successfully imported {count} items"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error importing file: {str(e)}")


# ==================== PURCHASES ====================

@app.get("/api/purchases", response_model=List[PurchaseResponse])
async def get_purchases_endpoint(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all purchases, optionally filtered by date range."""
    if start_date and end_date:
        purchases = get_purchases_by_date_range(start_date, end_date)
    else:
        purchases = get_all_purchases()
    return [PurchaseResponse(**p) for p in purchases]


@app.post("/api/purchases", response_model=PurchaseResponse)
async def create_purchase_endpoint(purchase: PurchaseCreate, current_user: dict = Depends(get_current_user)):
    """Create a new purchase."""
    purchase_id = create_purchase(
        date=purchase.date,
        invoice_no=purchase.invoice_no,
        item_id=purchase.item_id,
        quantity=purchase.quantity,
        rate=purchase.rate
    )

    # Get the created purchase with item name
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, i.item_name
        FROM purchases p
        JOIN items i ON p.item_id = i.item_id
        WHERE p.purchase_id = ?
    """, (purchase_id,))
    result = cursor.fetchone()
    conn.close()

    return PurchaseResponse(**dict(result))


# ==================== SALES ====================

@app.get("/api/sales", response_model=List[SaleResponse])
async def get_sales_endpoint(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all sales, optionally filtered by date range."""
    if start_date and end_date:
        sales = get_sales_by_date_range(start_date, end_date)
    else:
        sales = get_all_sales()
    return [SaleResponse(**s) for s in sales]


@app.get("/api/sales/cashier/{cashier_name}", response_model=List[SaleResponse])
async def get_sales_by_cashier_endpoint(cashier_name: str, current_user: dict = Depends(get_current_user)):
    """Get sales by a specific cashier."""
    sales = get_sales_by_cashier(cashier_name)
    return [SaleResponse(**s) for s in sales]


@app.get("/api/sales/summary", response_model=List[CashierSummary])
async def get_cashier_summary_endpoint(current_user: dict = Depends(get_current_user)):
    """Get sales summary by cashier."""
    summary = get_cashier_summary()
    return [CashierSummary(**s) for s in summary]


@app.post("/api/sales", response_model=SaleResponse)
async def create_sale_endpoint(sale: SaleCreate, current_user: dict = Depends(get_current_user)):
    """Create a new sale."""
    sale_id = create_sale(
        date=sale.date,
        cashier_name=sale.cashier_name,
        shift=sale.shift,
        item_id=sale.item_id,
        quantity=sale.quantity
    )

    if sale_id is None:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock for this sale"
        )

    # Get the created sale with item name
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.*, i.item_name
        FROM sales s
        JOIN items i ON s.item_id = i.item_id
        WHERE s.sale_id = ?
    """, (sale_id,))
    result = cursor.fetchone()
    conn.close()

    return SaleResponse(**dict(result))


# ==================== PHYSICAL STOCK ====================

@app.get("/api/physical-stock", response_model=List[PhysicalStockResponse])
async def get_physical_stock_endpoint(current_user: dict = Depends(get_current_user)):
    """Get all physical stock entries."""
    entries = get_all_physical_stock()
    return [PhysicalStockResponse(**e) for e in entries]


@app.post("/api/physical-stock", response_model=PhysicalStockResponse)
async def create_physical_stock_endpoint(stock: PhysicalStockCreate, current_user: dict = Depends(get_current_user)):
    """Create a physical stock entry."""
    entry_id = create_physical_stock(
        date=stock.date,
        item_id=stock.item_id,
        physical_quantity=stock.physical_quantity
    )

    # Get the created entry with item name
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ps.*, i.item_name
        FROM physical_stock ps
        JOIN items i ON ps.item_id = i.item_id
        WHERE ps.entry_id = ?
    """, (entry_id,))
    result = cursor.fetchone()
    conn.close()

    return PhysicalStockResponse(**dict(result))


# ==================== REPORTS ====================

@app.get("/api/reports/stock-comparison", response_model=StockComparisonReport)
async def get_stock_comparison_report_endpoint(current_user: dict = Depends(get_current_user)):
    """Get stock comparison report."""
    report = generate_stock_comparison_report()
    return StockComparisonReport(**report)


@app.get("/api/reports/current-stock", response_model=List[CurrentStockItem])
async def get_current_stock_report_endpoint(current_user: dict = Depends(get_current_user)):
    """Get current stock report."""
    report = generate_current_stock_report()
    return [CurrentStockItem(**r) for r in report]


@app.get("/api/reports/sales")
async def get_sales_report_endpoint(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get sales report, optionally filtered by date range."""
    report = generate_sales_report(start_date, end_date)
    return report


@app.get("/api/reports/purchases")
async def get_purchase_report_endpoint(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get purchase report, optionally filtered by date range."""
    report = generate_purchase_report(start_date, end_date)
    return report


# ==================== HEALTH CHECK ====================

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Lubricant Inventory API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
