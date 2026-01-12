"""Update admin user role to ADMIN."""

import asyncio

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from cnm_bookhub_be.db.models import load_all_models
from cnm_bookhub_be.db.models.users import User
from cnm_bookhub_be.settings import settings


async def update_admin_role() -> None:
    """Update admin@example.com role to ADMIN."""
    # Load all models first
    load_all_models()

    # Create engine and session
    engine = create_async_engine(str(settings.db_url), echo=False)
    async_session = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    async with async_session() as session:
        try:
            # Update admin user role
            result = await session.execute(
                select(User).where(User.email == "admin@example.com")
            )
            admin_user = result.scalar_one_or_none()

            if admin_user:
                admin_user.role = "ADMIN"
                admin_user.is_superuser = True
                await session.commit()
                print(f"✅ Updated {admin_user.email} role to ADMIN")
            else:
                print("❌ Admin user not found")

            # Update all other users to have USER role if they don't have one
            result = await session.execute(
                select(User).where(
                    User.email != "admin@example.com",
                    User.role.is_(None),
                )
            )
            users = result.scalars().all()

            for user in users:
                user.role = "USER"
                print(f"✅ Updated {user.email} role to USER")

            await session.commit()
            print("\n✅ All users updated successfully!")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error updating users: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(update_admin_role())
