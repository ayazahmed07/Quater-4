"""
Seed script to create initial test data for the Fuel Pump Management System.
Run this after setting up the database.
"""
import asyncio
from decimal import Decimal
from app.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.customer import Customer, CustomerStatus
from app.models.product import Product, ProductType, FuelType, ProductUnit


async def seed_data():
    async with AsyncSessionLocal() as db:
        # Create Users
        admin = User(
            email="admin@test.com",
            password_hash=get_password_hash("admin123"),
            role="ADMIN",
        )
        cashier = User(
            email="cashier@test.com",
            password_hash=get_password_hash("cashier123"),
            role="CASHIER",
        )
        customer_user = User(
            email="customer@test.com",
            password_hash=get_password_hash("customer123"),
            role="CUSTOMER",
        )
        db.add_all([admin, cashier, customer_user])
        await db.flush()

        # Create Customer
        customer = Customer(
            user_id=customer_user.id,
            name="John Doe",
            phone="1234567890",
            address="123 Main St",
            credit_limit=Decimal("5000.00"),
            status=CustomerStatus.ACTIVE,
        )
        db.add(customer)
        await db.flush()

        # Create Products
        petrol = Product(
            name="Petrol",
            type=ProductType.FUEL,
            fuel_type=FuelType.PETROL,
            current_price=Decimal("1.50"),
            unit=ProductUnit.LITER,
        )
        hsd = Product(
            name="High Speed Diesel",
            type=ProductType.FUEL,
            fuel_type=FuelType.HSD,
            current_price=Decimal("1.35"),
            unit=ProductUnit.LITER,
        )
        hobc = Product(
            name="HOBC",
            type=ProductType.FUEL,
            fuel_type=FuelType.HOBC,
            current_price=Decimal("1.65"),
            unit=ProductUnit.LITER,
        )
        engine_oil = Product(
            name="Engine Oil 5W-30",
            type=ProductType.LUBRICANT,
            current_price=Decimal("25.00"),
            unit=ProductUnit.UNIT,
        )
        db.add_all([petrol, hsd, hobc, engine_oil])

        await db.commit()
        print("✅ Seed data created successfully!")
        print("\nDemo Accounts:")
        print("  Admin: admin@test.com / admin123")
        print("  Cashier: cashier@test.com / cashier123")
        print("  Customer: customer@test.com / customer123")


if __name__ == "__main__":
    asyncio.run(seed_data())
