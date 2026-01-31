"""
CRUD.PY - Database Operations
================================
All CRUD operations for the inventory system.
Supports both SQLite and PostgreSQL.
"""

import sqlite3
import pandas as pd
from typing import List, Optional, Dict
from database import USE_POSTGRES, DB_PATH

# Try to import PostgreSQL driver
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


# ==================== DATABASE ABSTRACTION ====================

def _get_connection():
    """Get database connection based on environment."""
    if USE_POSTGRES:
        DATABASE_URL = __import__('os').getenv("DATABASE_URL")
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = True
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn


def _execute_query(query: str, params: tuple = None, fetch: str = 'all'):
    """
    Execute a query and return results.
    fetch: 'all', 'one', 'none', 'lastrowid'
    """
    conn = _get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor) if USE_POSTGRES else conn.cursor()

    # Convert params to tuple if None
    if params is None:
        params = ()

    try:
        if USE_POSTGRES:
            # PostgreSQL uses %s placeholders
            query_pg = query.replace('?', '%s')
            cursor.execute(query_pg, params)
        else:
            # SQLite uses ? placeholders
            cursor.execute(query, params)

        if fetch == 'all':
            result = cursor.fetchall()
        elif fetch == 'one':
            result = cursor.fetchone()
        elif fetch == 'lastrowid':
            if USE_POSTGRES:
                cursor.execute("SELECT lastval()")
                result = cursor.fetchone()['lastval']
            else:
                result = cursor.lastrowid
        else:  # none
            conn.commit() if not USE_POSTGRES else None
            result = None

        return result
    finally:
        cursor.close()
        conn.close()


def _dict_from_row(row) -> Dict:
    """Convert database row to dictionary."""
    if row is None:
        return None
    if USE_POSTGRES:
        return dict(row)
    else:
        return dict(row) if isinstance(row, sqlite3.Row) else row


# ==================== ITEMS ====================

def create_item(item_name: str, grade: str, pack_size: float,
                purchase_price: float, sale_price: float, opening_stock: float = 0) -> int:
    """Create a new item and return its ID."""
    result = _execute_query("""
        INSERT INTO items (item_name, grade, pack_size, purchase_price, sale_price, opening_stock)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (item_name, grade, pack_size, purchase_price, sale_price, opening_stock), fetch='lastrowid')
    return result


def get_all_items() -> List[Dict]:
    """Get all items."""
    rows = _execute_query("SELECT * FROM items ORDER BY item_name")
    return [_dict_from_row(row) for row in rows]


def get_item_by_id(item_id: int) -> Optional[Dict]:
    """Get an item by ID."""
    row = _execute_query("SELECT * FROM items WHERE item_id = ?", (item_id,), fetch='one')
    return _dict_from_row(row)


def update_item(item_id: int, item_name: str, grade: str, pack_size: float,
                purchase_price: float, sale_price: float) -> bool:
    """Update an item."""
    _execute_query("""
        UPDATE items
        SET item_name = ?, grade = ?, pack_size = ?, purchase_price = ?, sale_price = ?
        WHERE item_id = ?
    """, (item_name, grade, pack_size, purchase_price, sale_price, item_id), fetch='none')
    return True


def delete_item(item_id: int) -> bool:
    """Delete an item."""
    _execute_query("DELETE FROM items WHERE item_id = ?", (item_id,), fetch='none')
    return True


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
    result = _execute_query("""
        INSERT INTO purchases (date, invoice_no, item_id, quantity, rate)
        VALUES (?, ?, ?, ?, ?)
    """, (date, invoice_no, item_id, quantity, rate), fetch='lastrowid')
    return result


def get_all_purchases() -> List[Dict]:
    """Get all purchases with item names."""
    rows = _execute_query("""
        SELECT p.*, i.item_name
        FROM purchases p
        JOIN items i ON p.item_id = i.item_id
        ORDER BY p.date DESC
    """)
    return [_dict_from_row(row) for row in rows]


def get_purchases_by_date_range(start_date: str, end_date: str) -> List[Dict]:
    """Get purchases within a date range."""
    rows = _execute_query("""
        SELECT p.*, i.item_name
        FROM purchases p
        JOIN items i ON p.item_id = i.item_id
        WHERE p.date BETWEEN ? AND ?
        ORDER BY p.date DESC
    """, (start_date, end_date))
    return [_dict_from_row(row) for row in rows]


def import_purchases_from_excel(df: pd.DataFrame) -> int:
    """Import purchases from Excel DataFrame."""
    count = 0
    errors = []

    for _, row in df.iterrows():
        try:
            # Get item by name
            result = _execute_query("SELECT item_id FROM items WHERE item_name = ?", (row['Item Name'],), fetch='one')

            if not result:
                errors.append(f"Item '{row['Item Name']}' not found")
                continue

            item_id = result['item_id'] if USE_POSTGRES else result[0]

            create_purchase(
                date=str(row['Date']),
                invoice_no=str(row['Invoice No']),
                item_id=item_id,
                quantity=float(row['Quantity']),
                rate=float(row['Rate'])
            )
            count += 1
        except Exception as e:
            errors.append(f"Error importing row: {e}")
            continue

    return count


# ==================== SALES ====================

def create_sale(date: str, cashier_name: str, shift: str, item_id: int, quantity: float) -> Optional[int]:
    """Create a new sale and return its ID. Returns None if insufficient stock."""
    # Check stock first
    current_stock = get_system_stock(item_id)

    if current_stock < quantity:
        return None  # Insufficient stock

    result = _execute_query("""
        INSERT INTO sales (date, cashier_name, shift, item_id, quantity)
        VALUES (?, ?, ?, ?, ?)
    """, (date, cashier_name, shift, item_id, quantity), fetch='lastrowid')
    return result


def get_all_sales() -> List[Dict]:
    """Get all sales with item names."""
    rows = _execute_query("""
        SELECT s.*, i.item_name
        FROM sales s
        JOIN items i ON s.item_id = i.item_id
        ORDER BY s.date DESC
    """)
    return [_dict_from_row(row) for row in rows]


def get_sales_by_date_range(start_date: str, end_date: str) -> List[Dict]:
    """Get sales within a date range."""
    rows = _execute_query("""
        SELECT s.*, i.item_name
        FROM sales s
        JOIN items i ON s.item_id = i.item_id
        WHERE s.date BETWEEN ? AND ?
        ORDER BY s.date DESC
    """, (start_date, end_date))
    return [_dict_from_row(row) for row in rows]


def get_sales_by_cashier(cashier_name: str) -> List[Dict]:
    """Get sales by a specific cashier."""
    rows = _execute_query("""
        SELECT s.*, i.item_name
        FROM sales s
        JOIN items i ON s.item_id = i.item_id
        WHERE s.cashier_name = ?
        ORDER BY s.date DESC
    """, (cashier_name,))
    return [_dict_from_row(row) for row in rows]


def get_cashier_summary() -> List[Dict]:
    """Get sales summary by cashier."""
    rows = _execute_query("""
        SELECT
            cashier_name,
            SUM(quantity) as total_quantity,
            COUNT(*) as total_transactions
        FROM sales
        GROUP BY cashier_name
        ORDER BY cashier_name
    """)
    return [_dict_from_row(row) for row in rows]


def import_sales_from_excel(df: pd.DataFrame) -> int:
    """Import sales from Excel DataFrame."""
    count = 0
    errors = []

    for _, row in df.iterrows():
        try:
            # Get item by name
            result = _execute_query("SELECT item_id FROM items WHERE item_name = ?", (row['Item Name'],), fetch='one')

            if not result:
                errors.append(f"Item '{row['Item Name']}' not found")
                continue

            item_id = result['item_id'] if USE_POSTGRES else result[0]

            create_sale(
                date=str(row['Date']),
                cashier_name=str(row['Cashier']),
                shift=str(row['Cashier']),
                item_id=item_id,
                quantity=float(row['Quantity'])
            )
            count += 1
        except Exception as e:
            errors.append(f"Error importing row: {e}")
            continue

    return count


# ==================== PHYSICAL STOCK ====================

def create_physical_stock(date: str, item_id: int, physical_quantity: float) -> int:
    """Create a physical stock entry."""
    result = _execute_query("""
        INSERT INTO physical_stock (date, item_id, physical_quantity)
        VALUES (?, ?, ?)
    """, (date, item_id, physical_quantity), fetch='lastrowid')
    return result


def get_all_physical_stock() -> List[Dict]:
    """Get all physical stock entries."""
    rows = _execute_query("""
        SELECT ps.*, i.item_name
        FROM physical_stock ps
        JOIN items i ON ps.item_id = i.item_id
        ORDER BY ps.date DESC
    """)
    return [_dict_from_row(row) for row in rows]


def get_latest_physical_stock() -> Dict[int, float]:
    """Get the most recent physical count for each item."""
    rows = _execute_query("""
        SELECT item_id, physical_quantity
        FROM physical_stock ps1
        WHERE date = (
            SELECT MAX(date)
            FROM physical_stock ps2
            WHERE ps1.item_id = ps2.item_id
        )
    """)
    return {_dict_from_row(row)['item_id']: _dict_from_row(row)['physical_quantity'] for row in rows}


# ==================== STOCK CALCULATION ====================

def get_system_stock(item_id: int) -> float:
    """Calculate system stock for an item."""
    # Get opening stock
    result = _execute_query("SELECT opening_stock FROM items WHERE item_id = ?", (item_id,), fetch='one')
    opening_stock = _dict_from_row(result)['opening_stock'] if result else 0

    # Get total purchases
    result = _execute_query("SELECT COALESCE(SUM(quantity), 0) as total FROM purchases WHERE item_id = ?", (item_id,), fetch='one')
    total_purchases = _dict_from_row(result)['total'] if result else 0

    # Get total sales
    result = _execute_query("SELECT COALESCE(SUM(quantity), 0) as total FROM sales WHERE item_id = ?", (item_id,), fetch='one')
    total_sales = _dict_from_row(result)['total'] if result else 0

    return opening_stock + total_purchases - total_sales


def get_all_stock_summary() -> List[Dict]:
    """Get stock summary for all items."""
    items = get_all_items()
    summary = []

    for item in items:
        item_id = item['item_id']
        system_stock = get_system_stock(item_id)

        result = _execute_query("SELECT COALESCE(SUM(quantity), 0) as total FROM purchases WHERE item_id = ?", (item_id,), fetch='one')
        total_purchases = _dict_from_row(result)['total'] if result else 0

        result = _execute_query("SELECT COALESCE(SUM(quantity), 0) as total FROM sales WHERE item_id = ?", (item_id,), fetch='one')
        total_sales = _dict_from_row(result)['total'] if result else 0

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
