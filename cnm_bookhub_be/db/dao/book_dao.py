from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from cnm_bookhub_be.db.dependencies import get_db_session
from cnm_bookhub_be.db.models.books import Book

class BookDAO:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session
    
    # GET BOOKS BY CATEGORY ID
    async def get_books_category_id(self, category_id: int) -> list[Book]:
        """Lấy tất cả books theo category_id."""
        results = await self.session.execute(
            select(Book).where(Book.category_id == category_id),
        )
        return list(results.scalars().fetchall())