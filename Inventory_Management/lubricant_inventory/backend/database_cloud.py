"""
DATABASE_CLOUD.PY - PostgreSQL/SQLite Database Setup
====================================================
This file handles both PostgreSQL (production) and SQLite (development) database connections.
"""

import os
from contextlib import contextmanager
from typing import Generator, Dict, Any
import logging

# Try to import PostgreSQL driver, fallback to SQLite
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

import sqlite3

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Determine which database to use
USE_POSTGRES = DATABASE_URL and POSTGRES_AVAILABLE

# SQLite fallback for local development
if not USE_POSTGRES:
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    DB_PATH = DATA_DIR / "inventory.db"
    DATA_DIR.mkdir(exist_ok=True)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@contextmanager
def get_db() -> Generator:
    """
    Context manager for database connections.
    Supports both PostgreSQL and SQLite.
    """
    if USE_POSTGRES:
        # PostgreSQL connection
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    else:
        # SQLite connection
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
    if USE_POSTGRES:
        _init_postgres()
    else:
        _init_sqlite()


def _init_sqlite():
    """Initialize SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create USERS table
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
    logger.info(f"[OK] SQLite database initialized at: {DB_PATH}")


def _init_postgres():
    """Initialize PostgreSQL database."""
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = True
        cursor = conn.cursor()

        # Create USERS table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'cashier'
            )
        """)

        # Create ITEMS table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                item_id SERIAL PRIMARY KEY,
                item_name VARCHAR(255) NOT NULL,
                grade VARCHAR(100),
                pack_size REAL,
                purchase_price REAL NOT NULL,
                sale_price REAL NOT NULL,
                opening_stock REAL DEFAULT 0
            )
        """)

        # Create PURCHASES table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                purchase_id SERIAL PRIMARY KEY,
                date TEXT NOT NULL,
                invoice_no VARCHAR(255) NOT NULL,
                item_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                rate REAL NOT NULL,
                FOREIGN KEY (item_id) REFERENCES items (item_id)
            )
        """)

        # Create SALES table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                sale_id SERIAL PRIMARY KEY,
                date TEXT NOT NULL,
                cashier_name VARCHAR(255) NOT NULL,
                shift VARCHAR(50) NOT NULL,
                item_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                FOREIGN KEY (item_id) REFERENCES items (item_id)
            )
        """)

        # Create PHYSICAL_STOCK table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS physical_stock (
                entry_id SERIAL PRIMARY KEY,
                date TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                physical_quantity REAL NOT NULL,
                FOREIGN KEY (item_id) REFERENCES items (item_id)
            )
        """)

        cursor.close()
        conn.close()
        logger.info("[OK] PostgreSQL database initialized")
    except Exception as e:
        logger.error(f"Error initializing PostgreSQL: {e}")
        raise


def create_default_users():
    """Create default cashier accounts if they don't exist."""
    from auth import hash_password

    if USE_POSTGRES:
        _create_users_postgres()
    else:
        _create_users_sqlite()


def _create_users_sqlite():
    """Create default users in SQLite."""
    from auth import hash_password
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    if count == 0:
        password_hash = hash_password("cashier123")
        cursor.execute("""
            INSERT INTO users (username, password_hash, full_name, role)
            VALUES (?, ?, ?, ?)
        """, ("cashier1", password_hash, "Cashier 1", "cashier"))

        cursor.execute("""
            INSERT INTO users (username, password_hash, full_name, role)
            VALUES (?, ?, ?, ?)
        """, ("cashier2", password_hash, "Cashier 2", "cashier"))

        admin_hash = hash_password("admin123")
        cursor.execute("""
            INSERT INTO users (username, password_hash, full_name, role)
            VALUES (?, ?, ?, ?)
        """, ("admin", admin_hash, "Administrator", "admin"))

        conn.commit()
        logger.info("[OK] Default users created (SQLite)")
    else:
        logger.info("[OK] Users already exist (SQLite)")

    conn.close()


def _create_users_postgres():
    """Create default users in PostgreSQL."""
    from auth import hash_password
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]

        if count == 0:
            password_hash = hash_password("cashier123")
            cursor.execute("""
                INSERT INTO users (username, password_hash, full_name, role)
                VALUES (%s, %s, %s, %s)
            """, ("cashier1", password_hash, "Cashier 1", "cashier"))

            cursor.execute("""
                INSERT INTO users (username, password_hash, full_name, role)
                VALUES (%s, %s, %s, %s)
            """, ("cashier2", password_hash, "Cashier 2", "cashier"))

            admin_hash = hash_password("admin123")
            cursor.execute("""
                INSERT INTO users (username, password_hash, full_name, role)
                VALUES (%s, %s, %s, %s)
            """, ("admin", admin_hash, "Administrator", "admin"))

            logger.info("[OK] Default users created (PostgreSQL)")
        else:
            logger.info("[OK] Users already exist (PostgreSQL)")

        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error creating users in PostgreSQL: {e}")
        raise


if __name__ == "__main__":
    logger.info(f"Using {'PostgreSQL' if USE_POSTGRES else 'SQLite'} database")
    init_db()
    create_default_users()
