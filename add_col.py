import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from cnm_bookhub_be.settings import settings

async def add_column():
    # Attempting to use the settings provided in the environment/logs
    # Host: localhost, Port: 3306, User: root, Pass: root, Base: cn_bookhub
    db_url = "mysql+aiomysql://root:root@localhost:3306/cn_bookhub"
    print(f"Connecting to {db_url}...")
    engine = create_async_engine(db_url)
    try:
        async with engine.begin() as conn:
            print("Adding column 'description' to 'categories'...")
            await conn.execute(text("ALTER TABLE categories ADD COLUMN description VARCHAR(500) NULL"))
            print("Successfully added column!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_column())
