"""Seed script to populate orders and order items for testing."""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from cnm_bookhub_be.db.models import load_all_models
from cnm_bookhub_be.db.models.books import Book
from cnm_bookhub_be.db.models.order_items import OrderItem
from cnm_bookhub_be.db.models.orders import Order, OrderStatus
from cnm_bookhub_be.db.models.users import User
from cnm_bookhub_be.settings import settings


async def seed_orders() -> None:
    """Seed orders and order items into database."""
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
            # 1. Get the superuser
            print("🔍 Finding superuser...")  # noqa: T201
            result = await session.execute(
                select(User).where(User.email == "admin@example.com")  # type: ignore
            )
            user = result.unique().scalar_one_or_none()

            if not user:
                print("❌ Superuser not found! Please run seed.py first.")  # noqa: T201
                return

            print(f"✅ Found user: {user.email}")  # noqa: T201

            # 2. Get all books
            print("📚 Finding books...")  # noqa: T201
            result = await session.execute(select(Book).limit(5))
            books = list(result.scalars().fetchall())

            if not books:
                print("❌ No books found! Please run seed.py first.")  # noqa: T201
                return

            print(f"✅ Found {len(books)} books")  # noqa: T201

            # 3. Create sample orders
            print("\n📦 Creating orders...")  # noqa: T201

            # Check if orders already exist
            result = await session.execute(
                select(Order).where(Order.user_id == user.id).limit(1)
            )
            existing_order = result.scalar_one_or_none()

            orders_created = 0

            if not existing_order:
                order1 = Order(
                    user_id=user.id,
                    status=OrderStatus.COMPLETED.value,
                    address_at_purchase="123 Nguyen Hue, District 1, Ho Chi Minh City",
                    total_price=0,  # Will be calculated after adding items
                )
                session.add(order1)
                await session.flush()

                # Add 2 items to order 1
                order1_item1 = OrderItem(
                    order_id=order1.id,
                    book_id=books[0].id,
                    quantity=2,
                    price_at_purchase=books[0].price,
                )
                order1_item2 = OrderItem(
                    order_id=order1.id,
                    book_id=books[1].id,
                    quantity=1,
                    price_at_purchase=books[1].price,
                )
                session.add(order1_item1)
                session.add(order1_item2)
                await session.flush()

                # Calculate total_price for order 1
                order1.total_price = (
                    order1_item1.quantity * order1_item1.price_at_purchase
                    + order1_item2.quantity * order1_item2.price_at_purchase
                )
                print(
                    f"   ✓ Order 1: {order1.status} - 2 items - Total: {order1.total_price:,} VNĐ"
                )  # noqa: T201
                orders_created += 1

                # Order 2: Pending order from 3 days ago
                order2 = Order(
                    user_id=user.id,
                    status=OrderStatus.WAITING_FOR_CONFIRMATION.value,
                    address_at_purchase="456 Le Loi, District 3, Ho Chi Minh City",
                    total_price=0,  # Will be calculated after adding items
                )
                session.add(order2)
                await session.flush()

                # Add 3 items to order 2
                order2_item1 = OrderItem(
                    order_id=order2.id,
                    book_id=books[2].id,
                    quantity=1,
                    price_at_purchase=books[2].price,
                )
                order2_item2 = OrderItem(
                    order_id=order2.id,
                    book_id=books[3].id,
                    quantity=2,
                    price_at_purchase=books[3].price,
                )
                order2_item3 = OrderItem(
                    order_id=order2.id,
                    book_id=books[4].id,
                    quantity=1,
                    price_at_purchase=books[4].price,
                )
                session.add(order2_item1)
                session.add(order2_item2)
                session.add(order2_item3)
                await session.flush()

                # Calculate total_price for order 2
                order2.total_price = (
                    order2_item1.quantity * order2_item1.price_at_purchase
                    + order2_item2.quantity * order2_item2.price_at_purchase
                    + order2_item3.quantity * order2_item3.price_at_purchase
                )
                print(
                    f"   ✓ Order 2: {order2.status} - 3 items - Total: {order2.total_price:,} VNĐ"
                )  # noqa: T201
                orders_created += 1

                # Order 3: Shipped order from 5 days ago
                order3 = Order(
                    user_id=user.id,
                    status=OrderStatus.COMPLETED.value,
                    address_at_purchase="789 Tran Hung Dao, District 5, Ho Chi Minh City",
                    total_price=0,  # Will be calculated after adding items
                )
                session.add(order3)
                await session.flush()

                # Add 1 item to order 3
                order3_item1 = OrderItem(
                    order_id=order3.id,
                    book_id=books[0].id,
                    quantity=3,
                    price_at_purchase=books[0].price,
                )
                session.add(order3_item1)
                await session.flush()

                # Calculate total_price for order 3
                order3.total_price = (
                    order3_item1.quantity * order3_item1.price_at_purchase
                )
                print(
                    f"   ✓ Order 3: {order3.status} - 1 item - Total: {order3.total_price:,} VNĐ"
                )  # noqa: T201
                orders_created += 1

                await session.commit()
                print(f"\n✅ Seed completed successfully!")  # noqa: T201
                print(f"   - Orders created: {orders_created}")  # noqa: T201
                print(f"   - Total order items: 6")  # noqa: T201
                print(f"   - User: {user.email}")  # noqa: T201
            else:
                print("⚠️  Orders already exist for this user, skipping...")  # noqa: T201

        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error seeding data: {e}")  # noqa: T201
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_orders())
