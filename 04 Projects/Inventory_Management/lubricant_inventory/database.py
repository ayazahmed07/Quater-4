"""
DATABASE.PY
============
This file handles the database connection and creates all tables.

SIMPLE EXPLANATION:
- SQLite is like a simple file-based database (like Excel)
- Connection: Opening the database file
- Cursor: Tool to execute commands
- Tables: We create 4 tables to store different types of data
"""

import sqlite3
import os
from pathlib import Path


# ========================================
# STEP 1: Define Database Location
# ========================================
# This will create the database file in the data folder
# The folder will be created if it doesn't exist
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "inventory.db"

# Make sure the data folder exists
DATA_DIR.mkdir(exist_ok=True)


# ========================================
# STEP 2: Database Connection Function
# ========================================
def get_connection():
    """
    Opens a connection to the SQLite database.

    THINK OF IT AS:
    - Like opening a file to read/write
    - Returns a connection object that we can use to run SQL commands

    RETURNS:
        connection: SQLite connection object
    """
    conn = sqlite3.connect(DB_PATH)

    # This allows us to access columns by name (like row['item_name'])
    conn.row_factory = sqlite3.Row

    return conn


# ========================================
# STEP 3: Create All Tables
# ========================================
def create_tables():
    """
    Creates all 4 tables in the database.

    THINK OF IT AS:
    - Creating 4 separate sheets in Excel
    - Each table stores specific information

    TABLES CREATED:
    1. ITEMS      - Master list of all lubricant products
    2. PURCHASES  - Record of all purchases from PSO
    3. SALES      - Record of all sales to customers
    4. PHYSICAL_STOCK - Weekly physical stock counts
    """

    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------
    # TABLE 1: ITEMS (Master Item List)
    # --------------------------------
    # This stores all lubricant products
    # Like a product catalog
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            -- AUTOINCREMENT means the ID increases automatically (1, 2, 3...)

            item_name TEXT NOT NULL,
            -- Name of the lubricant (e.g., "HP Lubricant")

            grade TEXT,
            -- Grade or type (e.g., "SAE 10W-40")

            pack_size REAL,
            -- Size in liters (e.g., 1.0, 4.0, 10.0)

            purchase_price REAL NOT NULL,
            -- Price at which we buy from PSO

            sale_price REAL NOT NULL,
            -- Price at which we sell to customers

            opening_stock REAL DEFAULT 0
            -- Initial stock quantity when starting the system
        )
    """)

    # --------------------------------
    # TABLE 2: PURCHASES (Purchase Records)
    # --------------------------------
    # This records all purchases from PSO
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,

            date TEXT NOT NULL,
            -- Date of purchase (stored as text like "2024-01-15")

            invoice_no TEXT NOT NULL,
            -- Invoice number from PSO

            item_id INTEGER NOT NULL,
            -- Which item was purchased (links to items table)

            quantity REAL NOT NULL,
            -- How many units were purchased

            rate REAL NOT NULL,
            -- Purchase rate per unit

            FOREIGN KEY (item_id) REFERENCES items (item_id)
            -- FOREIGN KEY means this item_id must exist in items table
        )
    """)

    # --------------------------------
    # TABLE 3: SALES (Sales Records)
    # --------------------------------
    # This records all sales to customers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,

            date TEXT NOT NULL,
            -- Date of sale

            cashier_name TEXT NOT NULL,
            -- Name of cashier (there are 2 cashiers)

            shift TEXT NOT NULL,
            -- Shift: "Morning" or "Evening"

            item_id INTEGER NOT NULL,
            -- Which item was sold

            quantity REAL NOT NULL,
            -- How many units were sold

            FOREIGN KEY (item_id) REFERENCES items (item_id)
        )
    """)

    # --------------------------------
    # TABLE 4: PHYSICAL_STOCK (Weekly Physical Counts)
    # --------------------------------
    # This records weekly physical stock verification
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS physical_stock (
            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,

            date TEXT NOT NULL,
            -- Date of physical count

            item_id INTEGER NOT NULL,
            -- Which item was counted

            physical_quantity REAL NOT NULL,
            -- Actual quantity found during physical count

            FOREIGN KEY (item_id) REFERENCES items (item_id)
        )
    """)

    # Save all changes to the database
    conn.commit()

    # Close the connection (like closing a file)
    conn.close()

    print("✓ All tables created successfully!")


# ========================================
# STEP 4: Initialize Database
# ========================================
def init_database():
    """
    Initialize the database by creating all tables.
    Call this function when the application starts.
    """
    create_tables()
    print(f"✓ Database initialized at: {DB_PATH}")


# ========================================
# MAIN BLOCK (For Testing)
# ========================================
# This code runs only when you run this file directly
# It will NOT run when this file is imported into another file
if __name__ == "__main__":
    init_database()
