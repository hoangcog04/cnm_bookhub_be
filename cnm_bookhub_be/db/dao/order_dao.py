import uuid

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cnm_bookhub_be.db.dependencies import get_db_session
from cnm_bookhub_be.db.models.orders import Order
from datetime import datetime, timezone
from sqlalchemy import select


class OrderDAO:
    """DAO for Order entity."""

    def __init__(
        self,
        session: AsyncSession = Depends(get_db_session),
    ) -> None:
        self.session = session

    async def create_order(
        self,
        user_id: uuid.UUID,
        status: str,
        address_at_purchase: str,
    ) -> Order:
        """
        Create a new order.
        """
        order = Order(
            user_id=user_id,
            status=status,
            address_at_purchase=address_at_purchase,
        )
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def get_all_orders(
        self,
        limit: int,
        offset: int,
    ) -> list[Order]:
        """
        Get all orders with pagination.
        """
        result = await self.session.execute(
            select(Order)
            .limit(limit)
            .offset(offset),
        )
        return list(result.scalars().fetchall())

    async def get_order_by_id(
        self,
        order_id: uuid.UUID,
    ) -> Order | None:
        """
        Get order by ID.
        """
        result = await self.session.execute(
            select(Order).where(Order.id == order_id),
        )
        return result.scalar_one_or_none()

    async def update_order(
        self,
        order_id: uuid.UUID,
        status: str | None = None,
        address_at_purchase: str | None = None,
    ) -> Order | None:
        """
        Update order.
        """
        order = await self.get_order_by_id(order_id)
        if order is None:
            return None

        if status is not None:
            order.status = status
        if address_at_purchase is not None:
            order.address_at_purchase = address_at_purchase

        await self.session.commit()
        await self.session.refresh(order)
        return order


    async def soft_delete_order(self, order_id: uuid.UUID) -> bool:
        result = await self.session.execute(
            select(Order).where(Order.id == order_id),
        )
        order = result.scalar_one_or_none()

        if order is None:
            return False

        order.deleted = True
        order.deleted_at = datetime.now(timezone.utc)

        await self.session.commit()
        return True
