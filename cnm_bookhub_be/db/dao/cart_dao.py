from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from cnm_bookhub_be.db.dependencies import get_db_session
from cnm_bookhub_be.db.models.books import Book
from cnm_bookhub_be.db.models.carts import Cart
from cnm_bookhub_be.web.api.carts.schema import CartItemDTO


class CartDAO:
    def __init__(
        self,
        session: AsyncSession = Depends(get_db_session),
    ) -> None:
        self.session = session

    async def get_user_cart(self, user_id):
        # Join với Book để lấy thông tin đầy đủ
        result = await self.session.execute(
            select(
                Cart.book_id,
                Cart.quantity,
                Book.title,
                Book.author,
                Book.price,
                Book.image_urls,
            )
            .join(Book, Cart.book_id == Book.id)
            .where(
                Cart.user_id == user_id,
                Cart.deleted.is_(False),
            )
        )
        # Trả về list of CartItemDTO với thông tin đầy đủ
        rows = result.all()
        return [
            CartItemDTO(
                book_id=row.book_id,
                quantity=int(row.quantity),  # Đảm bảo quantity là int
                title=row.title,
                author=row.author,
                price=int(row.price),  # Đảm bảo price là int
                image_urls=row.image_urls,
            )
            for row in rows
        ]

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

    async def clear_cart(self, user_id: UUID) -> None:
        await self.session.execute(
            delete(Cart).where(
                Cart.user_id == user_id,
            )
        )
        await self.session.commit()
