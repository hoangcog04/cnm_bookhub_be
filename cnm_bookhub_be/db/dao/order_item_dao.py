import uuid

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cnm_bookhub_be.db.dependencies import get_db_session
from cnm_bookhub_be.db.models.order_items import OrderItem


class OrderItemDAO:
    """DAO for order_items table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    async def create_order_item(
        self,
        order_id: uuid.UUID,
        book_id: uuid.UUID,
        quantity: int,
        price_at_purchase: int,
    ) -> None:
        self.session.add(
            OrderItem(
                order_id=order_id,
                book_id=book_id,
                quantity=quantity,
                price_at_purchase=price_at_purchase,
            )
        )

    async def get_all_order_items(
        self,
        limit: int,
        offset: int,
    ) -> list[OrderItem]:
        result = await self.session.execute(
            select(OrderItem).limit(limit).offset(offset),
        )
        return list(result.scalars().fetchall())

    async def get_order_item_by_id(
        self,
        order_item_id: uuid.UUID,
    ) -> OrderItem | None:
        result = await self.session.execute(
            select(OrderItem).where(OrderItem.id == order_item_id),
        )
        return result.scalar_one_or_none()

    async def get_order_items_by_order_id(
        self,
        order_id: uuid.UUID,
    ) -> list[OrderItem]:
        result = await self.session.execute(
            select(OrderItem).where(OrderItem.order_id == order_id),
        )
        return list(result.scalars().fetchall())

    async def update_order_item(
        self,
        order_item_id: uuid.UUID,
        quantity: int | None = None,
        price_at_purchase: int | None = None,
    ) -> OrderItem | None:
        order_item = await self.get_order_item_by_id(order_item_id)
        if order_item is None:
            return None

        if quantity is not None:
            order_item.quantity = quantity
        if price_at_purchase is not None:
            order_item.price_at_purchase = price_at_purchase

        await self.session.commit()
        await self.session.refresh(order_item)
        return order_item

    async def delete_order_item(
        self,
        order_item_id: uuid.UUID,
    ) -> bool:
        order_item = await self.get_order_item_by_id(order_item_id)
        if order_item is None:
            return False

        await self.session.delete(order_item)
        await self.session.commit()
        return True

    async def soft_delete_order_item(
        self,
        order_item_id: uuid.UUID,
    ) -> bool:
        order_item = await self.get_order_item_by_id(order_item_id)
        if order_item is None or order_item.deleted:
            return False

        order_item.deleted = True
        await self.session.commit()
        return True
