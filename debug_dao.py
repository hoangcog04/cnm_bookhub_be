import asyncio
import uuid
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from cnm_bookhub_be.settings import settings
from cnm_bookhub_be.db.dao.book_dao import BookDAO
from cnm_bookhub_be.db.dao.category_dao import CategoryDAO
from cnm_bookhub_be.db.models.books import Book
from cnm_bookhub_be.db.models.categories import Category

engine = create_async_engine(str(settings.db_url), echo=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def test_daos():
    async with SessionLocal() as session:
        book_dao = BookDAO(session)
        category_dao = CategoryDAO(session)
        
        print("Testing CategoryDAO.get_all_category...")
        try:
            cats, total = await category_dao.get_all_category(limit=10, offset=1)
            print(f"Success! Found {len(cats)} categories. Total pages: {total}")
            for cat in cats:
                # Test the property that I suspect might be failing
                print(f"  Category: {cat.name}, Books count property: {cat.number_of_books}")
        except Exception as e:
            print(f"CategoryDAO Error: {e}")
            import traceback
            traceback.print_exc()

        print("\nTesting BookDAO.get_books...")
        try:
            books, total = await book_dao.get_books(limit=10, offset=1)
            print(f"Success! Found {len(books)} books. Total pages: {total}")
            for book in books:
                print(f"  Book: {book.title}, Category: {book.category_name}")
        except Exception as e:
            print(f"BookDAO Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_daos())
