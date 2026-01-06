from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cnm_bookhub_be.db.dependencies import get_db_session
from cnm_bookhub_be.db.models.carts import Cart
from sqlalchemy import delete
from uuid import UUID


class CartDAO:
    def __init__(
        self,
        session: AsyncSession = Depends(get_db_session),
    ) -> None:
        self.session = session

    async def get_user_cart(self, user_id):
        result = await self.session.execute(
            select(Cart).where(
                Cart.user_id == user_id,
                Cart.deleted.is_(False),
            )
        )
        return list(result.scalars().all())

    async def add_or_increment(
        self,
        user_id,
        book_id,
        quantity: int,
    ) -> Cart:
        result = await self.session.execute(
            select(Cart).where(
                Cart.user_id == user_id,
                Cart.book_id == book_id,
            )
        )
        item = result.scalar_one_or_none()

        if item:
            item.quantity += quantity
        else:
            item = Cart(
                user_id=user_id,
                book_id=book_id,
                quantity=quantity,
            )
            self.session.add(item)

        await self.session.commit()
        return item

    async def update_quantity(
        self,
        user_id,
        book_id,
        quantity: int,
    ) -> Cart | None:
        result = await self.session.execute(
            select(Cart).where(
                Cart.user_id == user_id,
                Cart.book_id == book_id,
                Cart.deleted.is_(False),
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            return None

        item.quantity = quantity
        await self.session.commit()
        return item

    async def soft_delete(
        self,
        user_id,
        book_id,
    ) -> bool:
        result = await self.session.execute(
            select(Cart).where(
                Cart.user_id == user_id,
                Cart.book_id == book_id,
                Cart.deleted.is_(False),
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            return False

        item.deleted = True
        await self.session.commit()
        return True

    async def clear_cart(self, user_id):
        items = await self.get_user_cart(user_id)
        for item in items:
            item.deleted = True
        await self.session.commit()

    async def hard_delete(
            self,
            user_id: UUID,
            book_id: UUID,
        ) -> bool:
            result = await self.session.execute(
                delete(Cart).where(
                    Cart.user_id == user_id,
                    Cart.book_id == book_id,
                )
            )
            await self.session.commit()
            return result.rowcount > 0

