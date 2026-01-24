"""
Create inventory records for existing products.
"""
import asyncio
from decimal import Decimal
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.inventory import Inventory
from app.models.product import Product


async def create_inventory():
    async with AsyncSessionLocal() as db:
        # Get all products
        result = await db.execute(select(Product))
        products = result.scalars().all()

        for product in products:
            # Check if inventory exists
            inv_result = await db.execute(
                select(Inventory).where(Inventory.product_id == product.id)
            )
            existing = inv_result.scalar_one_or_none()

            if not existing:
                # Create inventory record
                inventory = Inventory(
                    product_id=product.id,
                    quantity=Decimal("1000.00") if product.type == "FUEL" else Decimal("50"),
                    low_stock_threshold=Decimal("100"),
                )
                db.add(inventory)
                print(f"Created inventory for {product.name}")

        await db.commit()
        print("✅ Inventory records created!")


if __name__ == "__main__":
    asyncio.run(create_inventory())
