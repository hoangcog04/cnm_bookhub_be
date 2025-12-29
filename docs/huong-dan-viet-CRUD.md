# Hướng dẫn viết CRUD API cho cnm_bookhub_be

## Cấu trúc thư mục

Project sử dụng kiến trúc **3-layer architecture**:

```
cnm_bookhub_be/
├── db/                          # Database layer
│   ├── models/                  # SQLAlchemy Models (Database tables)
│   │   ├── books.py
│   │   ├── categories.py
│   │   ├── orders.py
│   │   ├── users.py
│   │   └── ...
│   └── dao/                     # Data Access Objects (Business logic)
│       ├── dummy_dao.py
│       └── ...
└── web/
    └── api/                     # API layer
        ├── dummy/               # Ví dụ: API endpoint cho dummy
        │   ├── __init__.py
        │   ├── schema.py        # Pydantic schemas (Request/Response DTOs)
        │   └── views.py         # FastAPI routes/endpoints
        ├── users/
        ├── echo/
        └── router.py            # Main router - đăng ký tất cả routes
```

## Quy trình tạo CRUD cho một entity mới

Giả sử bạn muốn tạo CRUD cho **Books**. Đây là các bước:

### Bước 1: Tạo Database Model (nếu chưa có)

**File**: `cnm_bookhub_be/db/models/books.py`

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String, Integer, Numeric
from cnm_bookhub_be.db.base import Base

class BookModel(Base):
    """Model for books."""
    
    __tablename__ = "books"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(length=255))
    author: Mapped[str] = mapped_column(String(length=255))
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    # ... thêm các fields khác
```

> **Lưu ý**: Model này đã có sẵn trong `cnm_bookhub_be/db/models/books.py`, bạn có thể xem và chỉnh sửa nếu cần.

### Bước 2: Tạo DAO (Data Access Object)

**File**: `cnm_bookhub_be/db/dao/book_dao.py` (tạo mới)

```python
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cnm_bookhub_be.db.dependencies import get_db_session
from cnm_bookhub_be.db.models.books import BookModel


class BookDAO:
    """Class for accessing books table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    async def create_book(
        self, 
        title: str, 
        author: str, 
        price: float
    ) -> None:
        """
        Create a new book.
        
        :param title: book title.
        :param author: book author.
        :param price: book price.
        """
        self.session.add(BookModel(title=title, author=author, price=price))

    async def get_all_books(self, limit: int, offset: int) -> list[BookModel]:
        """
        Get all books with pagination.
        
        :param limit: limit of books.
        :param offset: offset of books.
        :return: list of books.
        """
        raw_books = await self.session.execute(
            select(BookModel).limit(limit).offset(offset),
        )
        return list(raw_books.scalars().fetchall())

    async def get_book_by_id(self, book_id: int) -> BookModel | None:
        """
        Get book by ID.
        
        :param book_id: book ID.
        :return: book model or None.
        """
        result = await self.session.execute(
            select(BookModel).where(BookModel.id == book_id),
        )
        return result.scalar_one_or_none()

    async def update_book(
        self, 
        book_id: int, 
        title: str | None = None,
        author: str | None = None,
        price: float | None = None,
    ) -> BookModel | None:
        """
        Update book by ID.
        
        :param book_id: book ID.
        :param title: new title.
        :param author: new author.
        :param price: new price.
        :return: updated book or None.
        """
        book = await self.get_book_by_id(book_id)
        if book is None:
            return None
        
        if title is not None:
            book.title = title
        if author is not None:
            book.author = author
        if price is not None:
            book.price = price
        
        await self.session.commit()
        await self.session.refresh(book)
        return book

    async def delete_book(self, book_id: int) -> bool:
        """
        Delete book by ID.
        
        :param book_id: book ID.
        :return: True if deleted, False if not found.
        """
        book = await self.get_book_by_id(book_id)
        if book is None:
            return False
        
        await self.session.delete(book)
        await self.session.commit()
        return True
```

### Bước 3: Tạo Pydantic Schemas (DTOs)

**File**: `cnm_bookhub_be/web/api/books/schema.py` (tạo mới folder `books` trước)

```python
from pydantic import BaseModel, ConfigDict


class BookDTO(BaseModel):
    """
    DTO for book models.
    
    Used when returning book data from API.
    """
    
    id: int
    title: str
    author: str
    price: float
    
    model_config = ConfigDict(from_attributes=True)


class BookInputDTO(BaseModel):
    """DTO for creating new book."""
    
    title: str
    author: str
    price: float


class BookUpdateDTO(BaseModel):
    """DTO for updating book."""
    
    title: str | None = None
    author: str | None = None
    price: float | None = None
```

### Bước 4: Tạo API Views (Routes/Endpoints)

**File**: `cnm_bookhub_be/web/api/books/views.py`

```python
from fastapi import APIRouter, HTTPException, status
from fastapi.param_functions import Depends

from cnm_bookhub_be.db.dao.book_dao import BookDAO
from cnm_bookhub_be.db.models.books import BookModel
from cnm_bookhub_be.web.api.books.schema import (
    BookDTO,
    BookInputDTO,
    BookUpdateDTO,
)

router = APIRouter()


@router.get("/", response_model=list[BookDTO])
async def get_books(
    limit: int = 10,
    offset: int = 0,
    book_dao: BookDAO = Depends(),
) -> list[BookModel]:
    """
    Retrieve all books from the database.
    
    :param limit: limit of books, defaults to 10.
    :param offset: offset of books, defaults to 0.
    :param book_dao: DAO for books.
    :return: list of books from database.
    """
    return await book_dao.get_all_books(limit=limit, offset=offset)


@router.get("/{book_id}", response_model=BookDTO)
async def get_book(
    book_id: int,
    book_dao: BookDAO = Depends(),
) -> BookModel:
    """
    Get book by ID.
    
    :param book_id: book ID.
    :param book_dao: DAO for books.
    :return: book from database.
    """
    book = await book_dao.get_book_by_id(book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    return book


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(
    new_book: BookInputDTO,
    book_dao: BookDAO = Depends(),
) -> None:
    """
    Create book in the database.
    
    :param new_book: new book data.
    :param book_dao: DAO for books.
    """
    await book_dao.create_book(
        title=new_book.title,
        author=new_book.author,
        price=new_book.price,
    )


@router.put("/{book_id}", response_model=BookDTO)
async def update_book(
    book_id: int,
    book_update: BookUpdateDTO,
    book_dao: BookDAO = Depends(),
) -> BookModel:
    """
    Update book in the database.
    
    :param book_id: book ID.
    :param book_update: book update data.
    :param book_dao: DAO for books.
    :return: updated book.
    """
    book = await book_dao.update_book(
        book_id=book_id,
        title=book_update.title,
        author=book_update.author,
        price=book_update.price,
    )
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    book_dao: BookDAO = Depends(),
) -> None:
    """
    Delete book from the database.
    
    :param book_id: book ID.
    :param book_dao: DAO for books.
    """
    success = await book_dao.delete_book(book_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
```

### Bước 5: Tạo __init__.py cho module books

**File**: `cnm_bookhub_be/web/api/books/__init__.py`

```python
"""API for managing books."""

from cnm_bookhub_be.web.api.books.views import router

__all__ = ["router"]
```

### Bước 6: Đăng ký router vào main router

**File**: `cnm_bookhub_be/web/api/router.py` (chỉnh sửa)

```python
from fastapi.routing import APIRouter

from cnm_bookhub_be.web.api import dummy, echo, monitoring, users, books  # Thêm books

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(users.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
api_router.include_router(books.router, prefix="/books", tags=["books"])  # Thêm dòng này
```

### Bước 7: Tạo migration (nếu model mới hoặc có thay đổi)

```bash
# Tạo migration tự động
alembic revision --autogenerate -m "Add books table"

# Chạy migration
alembic upgrade head
```

### Bước 8: Test API

Khởi động server:
```bash
uv run -m cnm_bookhub_be
```

Truy cập API docs: `http://localhost:8000/api/docs`

Bạn sẽ thấy endpoints:
- `GET /api/books/` - Lấy danh sách books
- `GET /api/books/{book_id}` - Lấy book theo ID
- `POST /api/books/` - Tạo book mới
- `PUT /api/books/{book_id}` - Cập nhật book
- `DELETE /api/books/{book_id}` - Xóa book

## Tóm tắt cấu trúc thư mục cho mỗi entity mới:

```
cnm_bookhub_be/
├── db/
│   ├── models/
│   │   └── <entity>.py          # SQLAlchemy model
│   └── dao/
│       └── <entity>_dao.py      # Data access object (CRUD logic)
└── web/
    └── api/
        ├── <entity>/
        │   ├── __init__.py
        │   ├── schema.py        # Pydantic DTOs
        │   └── views.py         # FastAPI routes
        └── router.py            # Đăng ký routes tại đây
```

## Best Practices

1. **Đặt tên file**: Sử dụng snake_case (ví dụ: `book_dao.py`, `order_item_dao.py`)
2. **Đặt tên class**: Sử dụng PascalCase (ví dụ: `BookDAO`, `BookModel`)
3. **Async/await**: Tất cả methods trong DAO và views đều là async
4. **Dependency injection**: Sử dụng `Depends()` để inject DAO và session
5. **HTTP status codes**: 
   - 200 OK - GET, PUT thành công
   - 201 Created - POST thành công
   - 204 No Content - DELETE thành công
   - 404 Not Found - Resource không tồn tại
6. **Error handling**: Dùng `HTTPException` để trả về lỗi

## Entities hiện có trong project

Dựa vào models đã có, bạn có thể tạo CRUD cho:
- ✅ `users` - Đã có
- ✅ `dummy_model` - Đã có (ví dụ tham khảo)
- 📝 `books` - Cần tạo
- 📝 `categories` - Cần tạo
- 📝 `orders` - Cần tạo
- 📝 `order_items` - Cần tạo
- 📝 `provinces` - Cần tạo
- 📝 `wards` - Cần tạo
- 📝 `social_accounts` - Cần tạo

Hãy bắt đầu với entity đơn giản như `categories` hoặc `books` để làm quen với quy trình! 🚀
