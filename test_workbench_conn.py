import os
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# Try to load .env if it exists
load_dotenv()

# You can manually set these for testing if .env is not updated yet
# os.environ["CNM_BOOKHUB_BE_DB_PORT"] = "3306"
# os.environ["CNM_BOOKHUB_BE_DB_HOST"] = "localhost"
# os.environ["CNM_BOOKHUB_BE_DB_USER"] = "root"
# os.environ["CNM_BOOKHUB_BE_DB_PASS"] = ""
# os.environ["CNM_BOOKHUB_BE_DB_BASE"] = "cnm_bookhub_be"

from cnm_bookhub_be.settings import settings

async def test_conn():
    print(f"--- Local MySQL Connection Test ---")
    print(f"Target URL: {settings.db_url}")
    
    engine = create_async_engine(str(settings.db_url))
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"Status: SUCCESS (Result: {result.scalar()})")
            print(f"Connection verified to local MySQL Workbench.")
    except Exception as e:
        print(f"Status: FAILED")
        print(f"Error details: {e}")
        print("\nSuggestions:")
        print("1. Kiểm tra xem MySQL Service đã chạy chưa.")
        print("2. Đảm bảo Username/Password trong .env là đúng.")
        print("3. Kiểm tra xem database đã được tạo trong Workbench chưa.")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_conn())
