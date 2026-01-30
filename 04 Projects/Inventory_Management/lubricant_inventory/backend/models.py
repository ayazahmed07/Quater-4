"""
MODELS.PY - Pydantic Models
============================
Request and response models for API validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime


# ==================== AUTH MODELS ====================

class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class UserResponse(BaseModel):
    """User response model."""
    user_id: int
    username: str
    full_name: str
    role: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==================== ITEM MODELS ====================

class ItemBase(BaseModel):
    """Base item model."""
    item_name: str
    grade: Optional[str] = ""
    pack_size: float = 1.0
    purchase_price: float
    sale_price: float


class ItemCreate(ItemBase):
    """Item creation model."""
    opening_stock: float = 0.0


class ItemUpdate(ItemBase):
    """Item update model."""
    pass


class ItemResponse(ItemBase):
    """Item response model."""
    item_id: int
    opening_stock: float

    class Config:
        from_attributes = True


class ItemStockResponse(BaseModel):
    """Item with current stock."""
    item_id: int
    item_name: str
    grade: Optional[str]
    pack_size: float
    opening_stock: float
    total_purchases: float
    total_sales: float
    system_stock: float
    sale_price: float


# ==================== PURCHASE MODELS ====================

class PurchaseBase(BaseModel):
    """Base purchase model."""
    date: str  # YYYY-MM-DD format
    invoice_no: str
    item_id: int
    quantity: float
    rate: float


class PurchaseCreate(PurchaseBase):
    """Purchase creation model."""
    pass


class PurchaseResponse(PurchaseBase):
    """Purchase response model."""
    purchase_id: int
    item_name: str

    class Config:
        from_attributes = True


# ==================== SALES MODELS ====================

class SaleBase(BaseModel):
    """Base sale model."""
    date: str  # YYYY-MM-DD format
    cashier_name: str
    shift: str  # "Morning" or "Evening"
    item_id: int
    quantity: float


class SaleCreate(SaleBase):
    """Sale creation model."""
    pass


class SaleResponse(SaleBase):
    """Sale response model."""
    sale_id: int
    item_name: str

    class Config:
        from_attributes = True


class CashierSummary(BaseModel):
    """Cashier performance summary."""
    cashier_name: str
    total_quantity: float
    total_transactions: int


# ==================== PHYSICAL STOCK MODELS ====================

class PhysicalStockBase(BaseModel):
    """Base physical stock model."""
    date: str  # YYYY-MM-DD format
    item_id: int
    physical_quantity: float


class PhysicalStockCreate(PhysicalStockBase):
    """Physical stock creation model."""
    pass


class PhysicalStockResponse(PhysicalStockBase):
    """Physical stock response model."""
    entry_id: int
    item_name: str

    class Config:
        from_attributes = True


# ==================== REPORT MODELS ====================

class StockComparisonItem(BaseModel):
    """Stock comparison item."""
    item_id: int
    item_name: str
    grade: Optional[str]
    pack_size: float
    opening_stock: float
    total_purchases: float
    total_sales: float
    system_stock: float
    physical_stock: Optional[float]
    difference: Optional[float]
    status: str
    rate: float
    value_impact: Optional[float]


class StockComparisonSummary(BaseModel):
    """Stock comparison summary."""
    total_items: int
    items_with_shortage: int
    items_with_excess: int
    items_matching: int
    items_no_count: int
    total_shortage_value: float
    total_excess_value: float


class StockComparisonReport(BaseModel):
    """Complete stock comparison report."""
    items: List[StockComparisonItem]
    summary: StockComparisonSummary


class CurrentStockItem(BaseModel):
    """Current stock item."""
    item_name: str
    grade: Optional[str]
    pack_size: float
    system_stock: float
    purchase_price: float
    sale_price: float
    stock_value: float


class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total_items: int
    total_purchases: float
    total_sales: float
    current_stock: float
