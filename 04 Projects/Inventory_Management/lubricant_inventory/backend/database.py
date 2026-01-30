"""
DATABASE.PY - SQLite Database Setup
===================================
This file handles database connection and creates all tables.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager


# Database path
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "inventory.db"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)


@contextmanager
def get_db():
    """
    Context manager for database connections.

    Yields a database connection and automatically closes it when done.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize the database and create all tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create USERS table (NEW - for authentication)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'cashier'
        )
    """)

    # Create ITEMS table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            grade TEXT,
            pack_size REAL,
            purchase_price REAL NOT NULL,
            sale_price REAL NOT NULL,
            opening_stock REAL DEFAULT 0
        )
    """)

    # Create PURCHASES table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            invoice_no TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            rate REAL NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items (item_id)
        )
    """)

    # Create SALES table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            cashier_name TEXT NOT NULL,
            shift TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items (item_id)
        )
    """)

    # Create PHYSICAL_STOCK table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS physical_stock (
            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            physical_quantity REAL NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items (item_id)
        )
    """)

    conn.commit()
    conn.close()

    print(f"✓ Database initialized at: {DB_PATH}")


def create_default_users():
    """Create default cashier accounts if they don't exist."""
    from auth import hash_password

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if users exist
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    if count == 0:
        # Create default cashiers
        password_hash = hash_password("cashier123")

        cursor.execute("""
            INSERT INTO users (username, password_hash, full_name, role)
            VALUES (?, ?, ?, ?)
        """, ("cashier1", password_hash, "Cashier 1", "cashier"))

        cursor.execute("""
            INSERT INTO users (username, password_hash, full_name, role)
            VALUES (?, ?, ?, ?)
        """, ("cashier2", password_hash, "Cashier 2", "cashier"))

        # Create admin user
        admin_hash = hash_password("admin123")
        cursor.execute("""
            INSERT INTO users (username, password_hash, full_name, role)
            VALUES (?, ?, ?, ?)
        """, ("admin", admin_hash, "Administrator", "admin"))

        conn.commit()
        print("✓ Default users created:")
        print("  - cashier1 / cashier123")
        print("  - cashier2 / cashier123")
        print("  - admin / admin123")
    else:
        print("✓ Users already exist, skipping default creation")

    conn.close()


if __name__ == "__main__":
    init_db()
    create_default_users()
