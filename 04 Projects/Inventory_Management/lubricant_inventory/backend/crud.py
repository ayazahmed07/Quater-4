"""
CRUD.PY - Database Operations
================================
All CRUD operations for the inventory system.
"""

import sqlite3
import pandas as pd
from typing import List, Optional, Dict
from database import DB_PATH


# ==================== ITEMS ====================

def create_item(item_name: str, grade: str, pack_size: float,
                purchase_price: float, sale_price: float, opening_stock: float = 0) -> int:
    """Create a new item and return its ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO items (item_name, grade, pack_size, purchase_price, sale_price, opening_stock)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (item_name, grade, pack_size, purchase_price, sale_price, opening_stock))

    conn.commit()
    item_id = cursor.lastrowid
    conn.close()

    return item_id


def get_all_items() -> List[Dict]:
    """Get all items."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM items ORDER BY item_name")
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_item_by_id(item_id: int) -> Optional[Dict]:
    """Get an item by ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM items WHERE item_id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def update_item(item_id: int, item_name: str, grade: str, pack_size: float,
                purchase_price: float, sale_price: float) -> bool:
    """Update an item."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE items
        SET item_name = ?, grade = ?, pack_size = ?, purchase_price = ?, sale_price = ?
        WHERE item_id = ?
    """, (item_name, grade, pack_size, purchase_price, sale_price, item_id))

    conn.commit()
    success = cursor.rowcount > 0
    conn.close()

    return success


def delete_item(item_id: int) -> bool:
    """Delete an item."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM items WHERE item_id = ?", (item_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()

    return success


def import_items_from_excel(df: pd.DataFrame) -> int:
    """Import items from Excel DataFrame."""
    count = 0

    for _, row in df.iterrows():
        try:
            create_item(
                item_name=row['Item Name'],
                grade=row.get('Grade', ''),
                pack_size=float(row.get('Pack Size', 1)),
                purchase_price=float(row['Purchase Price']),
                sale_price=float(row['Sale Price']),
                opening_stock=float(row.get('Opening Stock', 0))
            )
            count += 1
        except Exception as e:
            print(f"Error importing row: {e}")
            continue

    return count


# ==================== PURCHASES ====================

def create_purchase(date: str, invoice_no: str, item_id: int, quantity: float, rate: float) -> int:
    """Create a new purchase and return its ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO purchases (date, invoice_no, item_id, quantity, rate)
        VALUES (?, ?, ?, ?, ?)
    """, (date, invoice_no, item_id, quantity, rate))

    conn.commit()
    purchase_id = cursor.lastrowid
    conn.close()

    return purchase_id


def get_all_purchases() -> List[Dict]:
    """Get all purchases with item names."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.*, i.item_name
        FROM purchases p
        JOIN items i ON p.item_id = i.item_id
        ORDER BY p.date DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_purchases_by_date_range(start_date: str, end_date: str) -> List[Dict]:
    """Get purchases within a date range."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.*, i.item_name
        FROM purchases p
        JOIN items i ON p.item_id = i.item_id
        WHERE p.date BETWEEN ? AND ?
        ORDER BY p.date DESC
    """, (start_date, end_date))
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ==================== SALES ====================

def create_sale(date: str, cashier_name: str, shift: str, item_id: int, quantity: float) -> Optional[int]:
    """Create a new sale and return its ID. Returns None if insufficient stock."""
    # Check stock first
    current_stock = get_system_stock(item_id)

    if current_stock < quantity:
        return None  # Insufficient stock

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sales (date, cashier_name, shift, item_id, quantity)
        VALUES (?, ?, ?, ?, ?)
    """, (date, cashier_name, shift, item_id, quantity))

    conn.commit()
    sale_id = cursor.lastrowid
    conn.close()

    return sale_id


def get_all_sales() -> List[Dict]:
    """Get all sales with item names."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.*, i.item_name
        FROM sales s
        JOIN items i ON s.item_id = i.item_id
        ORDER BY s.date DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_sales_by_date_range(start_date: str, end_date: str) -> List[Dict]:
    """Get sales within a date range."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.*, i.item_name
        FROM sales s
        JOIN items i ON s.item_id = i.item_id
        WHERE s.date BETWEEN ? AND ?
        ORDER BY s.date DESC
    """, (start_date, end_date))
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_sales_by_cashier(cashier_name: str) -> List[Dict]:
    """Get sales by a specific cashier."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.*, i.item_name
        FROM sales s
        JOIN items i ON s.item_id = i.item_id
        WHERE s.cashier_name = ?
        ORDER BY s.date DESC
    """, (cashier_name,))
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_cashier_summary() -> List[Dict]:
    """Get sales summary by cashier."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            cashier_name,
            SUM(quantity) as total_quantity,
            COUNT(*) as total_transactions
        FROM sales
        GROUP BY cashier_name
        ORDER BY cashier_name
    """)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ==================== PHYSICAL STOCK ====================

def create_physical_stock(date: str, item_id: int, physical_quantity: float) -> int:
    """Create a physical stock entry."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO physical_stock (date, item_id, physical_quantity)
        VALUES (?, ?, ?)
    """, (date, item_id, physical_quantity))

    conn.commit()
    entry_id = cursor.lastrowid
    conn.close()

    return entry_id


def get_all_physical_stock() -> List[Dict]:
    """Get all physical stock entries."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ps.*, i.item_name
        FROM physical_stock ps
        JOIN items i ON ps.item_id = i.item_id
        ORDER BY ps.date DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_latest_physical_stock() -> Dict[int, float]:
    """Get the most recent physical count for each item."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT item_id, physical_quantity
        FROM physical_stock ps1
        WHERE date = (
            SELECT MAX(date)
            FROM physical_stock ps2
            WHERE ps1.item_id = ps2.item_id
        )
    """)
    rows = cursor.fetchall()
    conn.close()

    return {row['item_id']: row['physical_quantity'] for row in rows}


# ==================== STOCK CALCULATION ====================

def get_system_stock(item_id: int) -> float:
    """Calculate system stock for an item."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get opening stock
    cursor.execute("SELECT opening_stock FROM items WHERE item_id = ?", (item_id,))
    result = cursor.fetchone()
    opening_stock = result['opening_stock'] if result else 0

    # Get total purchases
    cursor.execute("SELECT COALESCE(SUM(quantity), 0) as total FROM purchases WHERE item_id = ?", (item_id,))
    result = cursor.fetchone()
    total_purchases = result['total'] if result else 0

    # Get total sales
    cursor.execute("SELECT COALESCE(SUM(quantity), 0) as total FROM sales WHERE item_id = ?", (item_id,))
    result = cursor.fetchone()
    total_sales = result['total'] if result else 0

    conn.close()

    return opening_stock + total_purchases - total_sales


def get_all_stock_summary() -> List[Dict]:
    """Get stock summary for all items."""
    items = get_all_items()
    summary = []

    for item in items:
        item_id = item['item_id']
        system_stock = get_system_stock(item_id)

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT COALESCE(SUM(quantity), 0) as total FROM purchases WHERE item_id = ?", (item_id,))
        total_purchases = cursor.fetchone()['total']

        cursor.execute("SELECT COALESCE(SUM(quantity), 0) as total FROM sales WHERE item_id = ?", (item_id,))
        total_sales = cursor.fetchone()['total']

        conn.close()

        summary.append({
            'item_id': item_id,
            'item_name': item['item_name'],
            'grade': item['grade'],
            'pack_size': item['pack_size'],
            'opening_stock': item['opening_stock'],
            'total_purchases': total_purchases,
            'total_sales': total_sales,
            'system_stock': system_stock,
            'sale_price': item['sale_price']
        })

    return summary


# ==================== DASHBOARD STATS ====================

def get_dashboard_stats() -> Dict:
    """Get dashboard statistics."""
    items = get_all_items()
    purchases = get_all_purchases()
    sales = get_all_sales()

    return {
        'total_items': len(items),
        'total_purchases': sum([p['quantity'] for p in purchases]),
        'total_sales': sum([s['quantity'] for s in sales]),
        'current_stock': sum([get_system_stock(item['item_id']) for item in items])
    }
