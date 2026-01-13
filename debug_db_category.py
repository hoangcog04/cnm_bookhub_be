import asyncio
from cnm_bookhub_be.db.models.books import Book
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from cnm_bookhub_be.settings import settings

async def main():
    # FORCE 127.0.0.1
    settings.db_host = "127.0.0.1"
    
    with open("debug_output.txt", "w", encoding="utf-8") as f:
        try:
            f.write(f"--- DEBUGGING CONNECTION ---\n")
            f.write(f"DB URL: {settings.db_url}\n")
            f.flush()
        
            engine = create_async_engine(str(settings.db_url), echo=False)
            async_session = async_sessionmaker(engine, expire_on_commit=False)

            async with async_session() as session:
                f.write("--- DEBUGGING CATEGORY 1 ---\n")
                f.flush()
                try:
                    # 1. Check specifically category 1
                    stmt = select(Book).where(Book.category_id == 1)
                    result = await session.execute(stmt)
                    cat_books = result.scalars().all()
                    f.write(f"\nBooks in Category 1: {len(cat_books)}\n")
                    for b in cat_books:
                        f.write(f"Book ID: {b.id}, Title: {b.title}, Deleted: {b.deleted}\n")

                    if len(cat_books) == 0:
                         # Check ANY books
                         f.write("\nNo books in cat 1. Checking ALL books...\n")
                         res = await session.execute(select(Book).limit(5))
                         all_books = res.scalars().all()
                         f.write(f"Total books found (sample): {len(all_books)}\n")
                         for b in all_books:
                             f.write(f"Book: {b.title} (Cat: {b.category_id})\n")
                    f.flush()

                except Exception as e:
                    f.write(f"\nQUERY ERROR: {e}\n")
                    f.flush()

            await engine.dispose()
        except Exception as  e:
            f.write(f"CRITICAL ERROR: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())
