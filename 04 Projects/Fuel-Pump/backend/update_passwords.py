"""
Update existing user passwords to use new bcrypt hashes.
"""
import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User


async def update_passwords():
    async with AsyncSessionLocal() as db:
        # Get existing users
        result = await db.execute(select(User).where(User.email.in_(["admin@test.com", "cashier@test.com", "customer@test.com"])))
        users = result.scalars().all()

        for user in users:
            if user.email == "admin@test.com":
                user.password_hash = get_password_hash("admin123")
            elif user.email == "cashier@test.com":
                user.password_hash = get_password_hash("cashier123")
            elif user.email == "customer@test.com":
                user.password_hash = get_password_hash("customer123")
            print(f"Updated password for {user.email}")

        await db.commit()
        print("✅ Passwords updated successfully!")


if __name__ == "__main__":
    asyncio.run(update_passwords())
