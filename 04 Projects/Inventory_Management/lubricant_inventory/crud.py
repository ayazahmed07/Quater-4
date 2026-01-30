"""
CRUD.PY
========
CRUD stands for: Create, Read, Update, Delete
This file contains all functions to interact with the database.

SIMPLE EXPLANATION:
- CREATE: Insert new data (add item, add purchase, add sale)
- READ: Fetch data (get all items, get item by ID)
- UPDATE: Change existing data
- DELETE: Remove data (not used in this system to maintain records)
"""

import sqlite3
from datetime import datetime
from database import get_connection
import pandas as pd


# ============================================
# ITEMS TABLE OPERATIONS
# ============================================

def add_item(item_name, grade, pack_size, purchase_price, sale_price, opening_stock=0):
    """
    Add a new lubricant item to the items table.

    THINK OF IT AS:
    - Adding a new product to your catalog

    PARAMETERS:
        item_name: Name of the lubricant (e.g., "HP Lubricant")
        grade: Grade/type (e.g., "SAE 10W-40")
        pack_size: Size in liters (e.g., 1.0, 4.0, 10.0)
        purchase_price: Buying price from PSO
        sale_price: Selling price to customers
        opening_stock: Initial stock quantity (default 0)

    RETURNS:
        item_id: The ID of the newly created item
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO items (item_name, grade, pack_size, purchase_price, sale_price, opening_stock)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (item_name, grade, pack_size, purchase_price, sale_price, opening_stock))

    conn.commit()
    item_id = cursor.lastrowid
    conn.close()

    return item_id


def get_all_items():
    """
    Fetch all items from the items table.

    THINK OF IT AS:
    - Getting a list of all products in your catalog

    RETURNS:
        List of all items as dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM items ORDER BY item_name")
    rows = cursor.fetchall()
    conn.close()

    # Convert to list of dictionaries
    return [dict(row) for row in rows]


def get_item_by_id(item_id):
    """
    Fetch a single item by its ID.

    PARAMETERS:
        item_id: The ID of the item to fetch

    RETURNS:
        Item details as a dictionary, or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM items WHERE item_id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def update_item(item_id, item_name, grade, pack_size, purchase_price, sale_price):
    """
    Update an existing item's details.

    THINK OF IT AS:
    - Editing a product in your catalog

    NOTE: We don't update opening_stock to maintain data integrity
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE items
        SET item_name = ?, grade = ?, pack_size = ?,
            purchase_price = ?, sale_price = ?
        WHERE item_id = ?
    """, (item_name, grade, pack_size, purchase_price, sale_price, item_id))

    conn.commit()
    conn.close()


def import_items_from_excel(df):
    """
    Import items from an uploaded Excel file.

    THINK OF IT AS:
    - Bulk uploading products from an Excel sheet

    EXPECTED COLUMNS IN EXCEL:
        - Item Name
        - Grade
        - Pack Size
        - Purchase Price
        - Sale Price
        - Opening Stock

    PARAMETERS:
        df: Pandas DataFrame from the uploaded Excel file

    RETURNS:
        Number of items successfully imported
    """
    count = 0

    for _, row in df.iterrows():
        try:
            add_item(
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


# ============================================
# PURCHASES TABLE OPERATIONS
# ============================================

def add_purchase(date, invoice_no, item_id, quantity, rate):
    """
    Add a new purchase record.

    THINK OF IT AS:
    - Recording a purchase from PSO
    - This will automatically increase your stock

    PARAMETERS:
        date: Date of purchase (format: "YYYY-MM-DD")
        invoice_no: Invoice number from PSO
        item_id: Which item was purchased
        quantity: How many units were purchased
        rate: Purchase rate per unit
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO purchases (date, invoice_no, item_id, quantity, rate)
        VALUES (?, ?, ?, ?, ?)
    """, (date, invoice_no, item_id, quantity, rate))

    conn.commit()
    conn.close()


def get_all_purchases():
    """
    Fetch all purchase records.

    RETURNS:
        List of all purchases with item names (joined from items table)
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.*,
               i.item_name
        FROM purchases p
        JOIN items i ON p.item_id = i.item_id
        ORDER BY p.date DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_purchases_by_date_range(start_date, end_date):
    """
    Fetch purchases within a date range.

    PARAMETERS:
        start_date: Start date (format: "YYYY-MM-DD")
        end_date: End date (format: "YYYY-MM-DD")

    RETURNS:
        List of purchases in the date range
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.*,
               i.item_name
        FROM purchases p
        JOIN items i ON p.item_id = i.item_id
        WHERE p.date BETWEEN ? AND ?
        ORDER BY p.date DESC
    """, (start_date, end_date))
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ============================================
# SALES TABLE OPERATIONS
# ============================================

def add_sale(date, cashier_name, shift, item_id, quantity):
    """
    Add a new sale record.

    THINK OF IT AS:
    - Recording a sale to a customer
    - This will automatically decrease your stock

    PARAMETERS:
        date: Date of sale (format: "YYYY-MM-DD")
        cashier_name: Name of the cashier
        shift: "Morning" or "Evening"
        item_id: Which item was sold
        quantity: How many units were sold

    RETURNS:
        True if sale was recorded, False if insufficient stock
    """
    # First check if we have enough stock
    current_stock = get_system_stock(item_id)

    if current_stock < quantity:
        return False  # Not enough stock!

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sales (date, cashier_name, shift, item_id, quantity)
        VALUES (?, ?, ?, ?, ?)
    """, (date, cashier_name, shift, item_id, quantity))

    conn.commit()
    conn.close()

    return True


def get_all_sales():
    """
    Fetch all sale records.

    RETURNS:
        List of all sales with item names
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.*,
               i.item_name
        FROM sales s
        JOIN items i ON s.item_id = i.item_id
        ORDER BY s.date DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_sales_by_date_range(start_date, end_date):
    """
    Fetch sales within a date range.

    PARAMETERS:
        start_date: Start date (format: "YYYY-MM-DD")
        end_date: End date (format: "YYYY-MM-DD")

    RETURNS:
        List of sales in the date range
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.*,
               i.item_name
        FROM sales s
        JOIN items i ON s.item_id = i.item_id
        WHERE s.date BETWEEN ? AND ?
        ORDER BY s.date DESC
    """, (start_date, end_date))
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_sales_by_cashier(cashier_name):
    """
    Fetch all sales by a specific cashier.

    PARAMETERS:
        cashier_name: Name of the cashier

    RETURNS:
        List of sales by that cashier
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.*,
               i.item_name
        FROM sales s
        JOIN items i ON s.item_id = i.item_id
        WHERE s.cashier_name = ?
        ORDER BY s.date DESC
    """, (cashier_name,))
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ============================================
# PHYSICAL STOCK TABLE OPERATIONS
# ============================================

def add_physical_stock_entry(date, item_id, physical_quantity):
    """
    Add a physical stock count entry.

    THINK OF IT AS:
    - Recording the actual count from your weekly physical verification

    PARAMETERS:
        date: Date of physical count (format: "YYYY-MM-DD")
        item_id: Which item was counted
        physical_quantity: Actual quantity found
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO physical_stock (date, item_id, physical_quantity)
        VALUES (?, ?, ?)
    """, (date, item_id, physical_quantity))

    conn.commit()
    conn.close()


def get_all_physical_stock():
    """
    Fetch all physical stock entries.

    RETURNS:
        List of all physical stock records with item names
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ps.*,
               i.item_name
        FROM physical_stock ps
        JOIN items i ON ps.item_id = i.item_id
        ORDER BY ps.date DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_latest_physical_stock():
    """
    Fetch the most recent physical stock count for each item.

    THINK OF IT AS:
    - Getting the last physical count for each product

    RETURNS:
        Dictionary with item_id as key and physical quantity as value
    """
    conn = get_connection()
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


# ============================================
# STOCK CALCULATION FUNCTIONS
# ============================================

def get_system_stock(item_id):
    """
    Calculate the current system stock for an item.

    FORMULA:
    System Stock = Opening Stock + Total Purchases - Total Sales

    THINK OF IT AS:
    - What the computer THINKS you should have
    - Based on all your purchases and sales records

    PARAMETERS:
        item_id: Which item to calculate stock for

    RETURNS:
        Current system stock quantity
    """
    conn = get_connection()
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

    # Calculate system stock
    system_stock = opening_stock + total_purchases - total_sales

    return system_stock


def get_all_stock_summary():
    """
    Get stock summary for all items.

    RETURNS:
        List of dictionaries with:
        - item_id, item_name, grade, pack_size
        - opening_stock, total_purchases, total_sales
        - system_stock, sale_price
    """
    items = get_all_items()
    summary = []

    for item in items:
        item_id = item['item_id']
        system_stock = get_system_stock(item_id)

        # Get total purchases and sales for display
        conn = get_connection()
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
