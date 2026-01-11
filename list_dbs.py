import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from yarl import URL

async def list_dbs():
    # Connect without a specific DB first
    db_url = URL.build(
        scheme="mysql+aiomysql",
        host="127.0.0.1",
        port=3306,
        user="root",
        password="root",
    )
    engine = create_async_engine(str(db_url))
    try:
        async with engine.connect() as conn:
            res = await conn.execute(text('SHOW DATABASES'))
            dbs = [row[0] for row in res]
            print(f"Available databases: {dbs}")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(list_dbs())
