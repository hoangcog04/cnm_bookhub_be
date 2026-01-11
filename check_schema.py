import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from cnm_bookhub_be.settings import settings

async def check_db():
    engine = create_async_engine(str(settings.db_url))
    try:
        async with engine.connect() as conn:
            print("--- Table: categories ---")
            res = await conn.execute(text('DESCRIBE categories'))
            for row in res:
                print(row)
                
            print("\n--- Table: books ---")
            res = await conn.execute(text('DESCRIBE books'))
            for row in res:
                print(row)
    except Exception as e:
        print(f"Error checking DB: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_db())
