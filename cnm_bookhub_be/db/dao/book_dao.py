import uuid
from typing import List, Optional, Tuple

from fastapi import Depends
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from cnm_bookhub_be.db.dependencies import get_db_session
from cnm_bookhub_be.db.models.books import Book


class BookDAO:
    """DAO for Book entity."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    async def create_book(
        self,
        title: str,
        author: str,
        price: int,
        stock: int,
        image_urls: str | None,
        description: str | None,
        more_info: dict | None,
        category_id: int,
    ) -> Book:
        book = Book(
            title=title,
            author=author,
            price=price,
            stock=stock,
            image_urls=image_urls,
            description=description,
            more_info=more_info,
            category_id=category_id,
        )
        self.session.add(book)
        await self.session.commit()
        await self.session.refresh(book, ["category"])
        return book

    async def get_books(
        self,
        limit: int,
        offset: int,
        book_name: Optional[str] = None,
        category_id: Optional[int] = None,
    ) -> Tuple[List[Book], int]:
        query = (
            select(Book).options(joinedload(Book.category)).where(Book.deleted == False)
        )

        if book_name:
            query = query.where(
                or_(
                    Book.title.ilike(f"%{book_name}%"),
                    Book.author.ilike(f"%{book_name}%"),
                )
            )

        if category_id:
            query = query.where(Book.category_id == category_id)

        # Count total
        count_query = select(func.count(Book.id)).where(Book.deleted == False)
        total_res = await self.session.execute(count_query)
        total = total_res.scalar_one()

        # Pagination logic (offset 1-based from FE)
        skip = (offset - 1) * limit if offset > 0 else 0

        result = await self.session.execute(
            query.limit(limit).offset(skip).order_by(Book.id.desc()),
        )
        items = list(result.scalars().unique().all())

        total_pages = (total + limit - 1) // limit if limit > 0 else 1

        return items, total_pages

    async def get_book_by_id(
        self,
        book_id: uuid.UUID,
    ) -> Book | None:
        result = await self.session.execute(
            select(Book)
            .options(joinedload(Book.category))
            .where(
                Book.id == book_id,
                Book.deleted.is_(False),
            ),
        )
        return result.scalar_one_or_none()

    async def update_book(
        self,
        book_id: uuid.UUID,
        **kwargs,
    ) -> Book | None:
        book = await self.get_book_by_id(book_id)
        if book is None:
            return None

        for field, value in kwargs.items():
            if value is not None and hasattr(book, field):
                setattr(book, field, value)

        await self.session.commit()
        await self.session.refresh(book, ["category"])
        return book

    async def delete_book(
        self,
        book_id: uuid.UUID,
    ) -> bool:
        book = await self.get_book_by_id(book_id)
        if book is None:
            return False

        await self.session.delete(book)
        await self.session.commit()
        return True

    async def soft_delete_book(
        self,
        book_id: uuid.UUID,
    ) -> bool:
        result = await self.session.execute(
            select(Book).where(
                Book.id == book_id,
                Book.deleted.is_(False),
            ),
        )
        book = result.scalar_one_or_none()
        if book is None:
            return False

        book.deleted = True
        await self.session.commit()
        return True

    # GET BOOKS BY CATEGORY ID
    async def get_books_category_id(self, category_id: int) -> list[Book]:
        """Lấy tất cả books theo category_id."""
        results = await self.session.execute(
            select(Book).where(Book.category_id == category_id),
        )
        return list(results.scalars().fetchall())
