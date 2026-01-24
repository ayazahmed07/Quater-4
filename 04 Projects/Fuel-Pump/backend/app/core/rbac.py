from enum import Enum
from typing import List, Set
from fastapi import HTTPException, status


class Role(str, Enum):
    ADMIN = "ADMIN"
    CASHIER = "CASHIER"
    CUSTOMER = "CUSTOMER"


class Permission(str, Enum):
    # User permissions
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    VIEW_USERS = "view_users"

    # Customer permissions
    CREATE_CUSTOMER = "create_customer"
    UPDATE_CUSTOMER = "update_customer"
    DELETE_CUSTOMER = "delete_customer"
    VIEW_CUSTOMERS = "view_customers"
    VIEW_OWN_PROFILE = "view_own_profile"

    # Product permissions
    CREATE_PRODUCT = "create_product"
    UPDATE_PRODUCT = "update_product"
    DELETE_PRODUCT = "delete_product"
    VIEW_PRODUCTS = "view_products"
    UPDATE_PRICE = "update_price"

    # Transaction permissions
    CREATE_TRANSACTION = "create_transaction"
    CONFIRM_TRANSACTION = "confirm_transaction"
    REJECT_TRANSACTION = "reject_transaction"
    VIEW_PENDING_TRANSACTIONS = "view_pending_transactions"
    VIEW_ALL_TRANSACTIONS = "view_all_transactions"
    VIEW_OWN_TRANSACTIONS = "view_own_transactions"

    # Invoice permissions
    GENERATE_INVOICE = "generate_invoice"
    VIEW_INVOICES = "view_invoices"
    VIEW_OWN_INVOICES = "view_own_invoices"
    RECORD_PAYMENT = "record_payment"

    # Inventory permissions
    VIEW_INVENTORY = "view_inventory"
    ADJUST_INVENTORY = "adjust_inventory"

    # Meter permissions
    CREATE_METER_READING = "create_meter_reading"
    VIEW_METER_READINGS = "view_meter_readings"

    # Report permissions
    VIEW_REPORTS = "view_reports"


# Role-Permission Mapping
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        # Full permissions
        Permission.CREATE_USER, Permission.UPDATE_USER, Permission.DELETE_USER, Permission.VIEW_USERS,
        Permission.CREATE_CUSTOMER, Permission.UPDATE_CUSTOMER, Permission.DELETE_CUSTOMER, Permission.VIEW_CUSTOMERS,
        Permission.CREATE_PRODUCT, Permission.UPDATE_PRODUCT, Permission.DELETE_PRODUCT, Permission.VIEW_PRODUCTS, Permission.UPDATE_PRICE,
        Permission.CREATE_TRANSACTION, Permission.CONFIRM_TRANSACTION, Permission.REJECT_TRANSACTION,
        Permission.VIEW_PENDING_TRANSACTIONS, Permission.VIEW_ALL_TRANSACTIONS,
        Permission.GENERATE_INVOICE, Permission.VIEW_INVOICES, Permission.RECORD_PAYMENT,
        Permission.VIEW_INVENTORY, Permission.ADJUST_INVENTORY,
        Permission.CREATE_METER_READING, Permission.VIEW_METER_READINGS,
        Permission.VIEW_REPORTS,
    },
    Role.CASHIER: {
        Permission.VIEW_PRODUCTS,
        Permission.VIEW_CUSTOMERS,
        Permission.CREATE_TRANSACTION,
        Permission.VIEW_PENDING_TRANSACTIONS,
        Permission.CREATE_METER_READING,
        Permission.VIEW_METER_READINGS,
    },
    Role.CUSTOMER: {
        Permission.VIEW_OWN_PROFILE,
        Permission.VIEW_OWN_TRANSACTIONS,
        Permission.VIEW_OWN_INVOICES,
    },
}


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())


def require_permission(role: Role, required_permission: Permission):
    if not has_permission(role, required_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission '{required_permission}' required",
        )
