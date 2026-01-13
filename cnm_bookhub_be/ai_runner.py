# File: cnm_bookhub_be/ai_runner.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

# Import các logic AI của bạn
from cnm_bookhub_be.ai.router import router as ai_router, BOOKS_CACHE, USER_SESSIONS, VALID_CATEGORIES_CACHE
from cnm_bookhub_be.ai.services.db_service import get_all_books_from_mysql, get_unique_categories
from cnm_bookhub_be.ai.services.chroma_service import add_books_to_chroma
from cnm_bookhub_be.settings import settings

# --- LIFESPAN RIÊNG CHO AI (Chỉ nạp AI, không nạp thừa thãi) ---
def init_ai_data_sync():
    """Hàm nạp dữ liệu (Chạy ở luồng phụ)"""
    print("🚀 AI Service: Bắt đầu nạp dữ liệu...")
    try:
        # 1. Load Sách từ DB (Dùng chung DB với Main App OK)
        raw_books = get_all_books_from_mysql()
        
        # 2. Nạp RAM
        BOOKS_CACHE.clear()
        for book in raw_books:
            BOOKS_CACHE[str(book['id'])] = book
            
        # 3. Nạp Chroma
        add_books_to_chroma(raw_books)
        
        # 4. Load Danh mục
        cats = get_unique_categories()
        VALID_CATEGORIES_CACHE.clear()
        VALID_CATEGORIES_CACHE.extend(cats)
        
        print(f"✅ AI Service: Sẵn sàng phục vụ {len(raw_books)} sách!")
    except Exception as e:
        print(f"❌ AI Init Error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tách luồng nạp dữ liệu để AI server khởi động nhanh
    asyncio.create_task(asyncio.to_thread(init_ai_data_sync))
    yield
    print("🛑 AI Service stopping...")
    USER_SESSIONS.clear()
    BOOKS_CACHE.clear()

# --- TẠO APP RIÊNG ---
app = FastAPI(title="BookHub AI Service", lifespan=lifespan)

# Cấu hình CORS (Để Frontend gọi được từ port khác)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn Router Chat
app.include_router(ai_router)

# --- ĐIỂM KHỞI CHẠY ---
if __name__ == "__main__":
    # Chạy ở Port 8001 (Khác port 8000 của Main App)
    uvicorn.run(
        "cnm_bookhub_be.ai_runner:app", 
        host="0.0.0.0", 
        port=8001, 
        reload=True
    )