import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from cnm_bookhub_be.settings import settings

async def check_cols():
    engine = create_async_engine(str(settings.db_url))
    try:
        async with engine.connect() as conn:
            res = await conn.execute(text('DESCRIBE categories'))
            cols = [row[0] for row in res]
            print(f"Categories columns: {cols}")
    except Exception as e:
        print(f"ERROR: {str(e)[:200]}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_cols())
