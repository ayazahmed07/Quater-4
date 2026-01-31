"""
AUTH.PY - JWT Authentication
=============================
Handles password hashing, token generation, and authentication.
Supports both SQLite and PostgreSQL.
"""

from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import JWTError, jwt
import sqlite3

from database import USE_POSTGRES, DB_PATH

# Try to import PostgreSQL driver
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


# Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"  # In production, use environment variable!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify a JWT token and return the payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    Authenticate a user by username and password.

    Returns user dict if successful, None otherwise.
    """
    if USE_POSTGRES:
        return _authenticate_user_postgres(username, password)
    else:
        return _authenticate_user_sqlite(username, password)


def _authenticate_user_sqlite(username: str, password: str) -> Optional[dict]:
    """Authenticate user using SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    return {
        "user_id": user["user_id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"]
    }


def _authenticate_user_postgres(username: str, password: str) -> Optional[dict]:
    """Authenticate user using PostgreSQL."""
    DATABASE_URL = __import__('os').getenv("DATABASE_URL")

    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user:
            return None

        if not verify_password(password, user["password_hash"]):
            return None

        return {
            "user_id": user["user_id"],
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get a user by ID."""
    if USE_POSTGRES:
        return _get_user_by_id_postgres(user_id)
    else:
        return _get_user_by_id_sqlite(user_id)


def _get_user_by_id_sqlite(user_id: int) -> Optional[dict]:
    """Get user by ID using SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, username, full_name, role FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return None

    return {
        "user_id": user["user_id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"]
    }


def _get_user_by_id_postgres(user_id: int) -> Optional[dict]:
    """Get user by ID using PostgreSQL."""
    DATABASE_URL = __import__('os').getenv("DATABASE_URL")

    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT user_id, username, full_name, role FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if not user:
            return None

        return {
            "user_id": user["user_id"],
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
    except Exception as e:
        print(f"Error getting user: {e}")
        return None
