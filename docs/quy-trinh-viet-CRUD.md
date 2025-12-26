# Quy trình viết CRUD - Hướng dẫn từng bước

> **Demo**: Categories CRUD đã hoàn thành - bạn có thể tham khảo các file đã tạo

## 📋 Quy trình 5 bước

### **Bước 1: Tạo DAO (Data Access Object)**

📁 **File**: `cnm_bookhub_be/db/dao/<entity>_dao.py`

**Mẫu code**:
```python
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cnm_bookhub_be.db.dependencies import get_db_session
from cnm_bookhub_be.db.models.<entity> import <EntityModel>


class <Entity>DAO:
    """Class for accessing <entity> table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    # CREATE
    async def create_<entity>(self, **fields) -> None:
        self.session.add(<EntityModel>(**fields))

    # READ ALL (with pagination)
    async def get_all_<entities>(self, limit: int, offset: int) -> list[<EntityModel>]:
        raw_items = await self.session.execute(
            select(<EntityModel>).limit(limit).offset(offset),
        )
        return list(raw_items.scalars().fetchall())

    # READ ONE by ID
    async def get_<entity>_by_id(self, id: int) -> <EntityModel> | None:
        result = await self.session.execute(
            select(<EntityModel>).where(<EntityModel>.id == id),
        )
        return result.scalar_one_or_none()

    # UPDATE
    async def update_<entity>(self, id: int, **fields) -> <EntityModel> | None:
        item = await self.get_<entity>_by_id(id)
        if item is None:
            return None
        
        for key, value in fields.items():
            if value is not None:
                setattr(item, key, value)
        
        await self.session.commit()
        await self.session.refresh(item)
        return item

    # DELETE
    async def delete_<entity>(self, id: int) -> bool:
        item = await self.get_<entity>_by_id(id)
        if item is None:
            return False
        
        await self.session.delete(item)
        await self.session.commit()
        return True
```

**Ví dụ thực tế**: [category_dao.py](file:///E:/SINHVIENIT/Year4_Ki1/TTCM%20Công%20nghệ%20mới/Project_CK/cnm_bookhub_be/cnm_bookhub_be/db/dao/category_dao.py)

---

### **Bước 2: Tạo Pydantic Schemas (DTOs)**

📁 **File**: `cnm_bookhub_be/web/api/<entity>/schema.py`

**Mẫu code**:
```python
from pydantic import BaseModel, ConfigDict


class <Entity>DTO(BaseModel):
    """DTO for <entity> response."""
    
    id: int
    field1: str
    field2: int
    # ... thêm các fields
    
    model_config = ConfigDict(from_attributes=True)


class <Entity>InputDTO(BaseModel):
    """DTO for creating <entity>."""
    
    field1: str
    field2: int
    # ... chỉ các fields cần thiết khi tạo mới


class <Entity>UpdateDTO(BaseModel):
    """DTO for updating <entity>."""
    
    field1: str | None = None
    field2: int | None = None
    # ... tất cả fields đều optional
```

**Ví dụ thực tế**: [schema.py](file:///E:/SINHVIENIT/Year4_Ki1/TTCM%20Công%20nghệ%20mới/Project_CK/cnm_bookhub_be/cnm_bookhub_be/web/api/categories/schema.py)

**Giải thích**:
- **DTO** = Response (trả về từ API, có `id`)
- **InputDTO** = Request khi tạo mới (không có `id`)
- **UpdateDTO** = Request khi update (tất cả fields optional)

---

### **Bước 3: Tạo API Views (Routes/Endpoints)**

📁 **File**: `cnm_bookhub_be/web/api/<entity>/views.py`

**Mẫu code**:
```python
from fastapi import APIRouter, HTTPException, status
from fastapi.param_functions import Depends

from cnm_bookhub_be.db.dao.<entity>_dao import <Entity>DAO
from cnm_bookhub_be.db.models.<entity> import <EntityModel>
from cnm_bookhub_be.web.api.<entity>.schema import (
    <Entity>DTO,
    <Entity>InputDTO,
    <Entity>UpdateDTO,
)

router = APIRouter()


# GET ALL - Lấy danh sách
@router.get("/", response_model=list[<Entity>DTO])
async def get_<entities>(
    limit: int = 10,
    offset: int = 0,
    dao: <Entity>DAO = Depends(),
) -> list[<EntityModel>]:
    return await dao.get_all_<entities>(limit=limit, offset=offset)


# GET ONE - Lấy theo ID
@router.get("/{id}", response_model=<Entity>DTO)
async def get_<entity>(
    id: int,
    dao: <Entity>DAO = Depends(),
) -> <EntityModel>:
    item = await dao.get_<entity>_by_id(id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="<Entity> not found",
        )
    return item


# POST - Tạo mới
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_<entity>(
    new_item: <Entity>InputDTO,
    dao: <Entity>DAO = Depends(),
) -> None:
    await dao.create_<entity>(**new_item.model_dump())


# PUT - Cập nhật
@router.put("/{id}", response_model=<Entity>DTO)
async def update_<entity>(
    id: int,
    update_data: <Entity>UpdateDTO,
    dao: <Entity>DAO = Depends(),
) -> <EntityModel>:
    item = await dao.update_<entity>(id=id, **update_data.model_dump(exclude_none=True))
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="<Entity> not found",
        )
    return item


# DELETE - Xóa
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_<entity>(
    id: int,
    dao: <Entity>DAO = Depends(),
) -> None:
    success = await dao.delete_<entity>(id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="<Entity> not found",
        )
```

**Ví dụ thực tế**: [views.py](file:///E:/SINHVIENIT/Year4_Ki1/TTCM%20Công%20nghệ%20mới/Project_CK/cnm_bookhub_be/cnm_bookhub_be/web/api/categories/views.py)

**HTTP Status Codes**:
- `200 OK` - GET, PUT thành công
- `201 Created` - POST thành công
- `204 No Content` - DELETE thành công
- `404 Not Found` - Resource không tồn tại

---

### **Bước 4: Tạo __init__.py**

📁 **File**: `cnm_bookhub_be/web/api/<entity>/__init__.py`

```python
"""API for managing <entities>."""

from cnm_bookhub_be.web.api.<entity>.views import router

__all__ = ["router"]
```

**Ví dụ thực tế**: [__init__.py](file:///E:/SINHVIENIT/Year4_Ki1/TTCM%20Công%20nghệ%20mới/Project_CK/cnm_bookhub_be/cnm_bookhub_be/web/api/categories/__init__.py)

---

### **Bước 5: Đăng ký Router**

📁 **File**: `cnm_bookhub_be/web/api/router.py`

**Thêm 2 dòng**:

```python
# 1. Import module
from cnm_bookhub_be.web.api import ..., <entity>

# 2. Đăng ký router
api_router.include_router(<entity>.router, prefix="/<entities>", tags=["<entities>"])
```

**Ví dụ thực tế**: [router.py](file:///E:/SINHVIENIT/Year4_Ki1/TTCM%20Công%20nghệ%20mới/Project_CK/cnm_bookhub_be/cnm_bookhub_be/web/api/router.py)

---

## ✅ Checklist khi viết CRUD

- [ ] **Bước 1**: Tạo `<entity>_dao.py` với 5 methods (create, get_all, get_by_id, update, delete)
- [ ] **Bước 2**: Tạo folder `<entity>/` trong `web/api/`
- [ ] **Bước 3**: Tạo `schema.py` với 3 DTOs (DTO, InputDTO, UpdateDTO)
- [ ] **Bước 4**: Tạo `views.py` với 5 endpoints (GET all, GET one, POST, PUT, DELETE)
- [ ] **Bước 5**: Tạo `__init__.py` export router
- [ ] **Bước 6**: Đăng ký router trong `router.py`
- [ ] **Bước 7**: Test API qua Swagger docs

---

## 🚀 Test CRUD API

### **1. Khởi động server**

```bash
uv run -m cnm_bookhub_be
```

### **2. Mở Swagger UI**

Truy cập: `http://localhost:8000/api/docs`

### **3. Test các endpoints**

Với Categories, bạn sẽ thấy:

```
GET    /api/categories/          - Lấy danh sách categories
GET    /api/categories/{id}      - Lấy category theo ID
POST   /api/categories/          - Tạo category mới
PUT    /api/categories/{id}      - Cập nhật category
DELETE /api/categories/{id}      - Xóa category
```

### **4. Thử nghiệm**

**Tạo category mới** (POST `/api/categories/`):
```json
{
  "name": "Fiction"
}
```

**Lấy tất cả** (GET `/api/categories/`):
```
Params: limit=10, offset=0
```

**Cập nhật** (PUT `/api/categories/1`):
```json
{
  "name": "Science Fiction"
}
```

**Xóa** (DELETE `/api/categories/1`)

---

## 📁 Cấu trúc files hoàn chỉnh

```
cnm_bookhub_be/
├── db/
│   ├── models/
│   │   └── categories.py         ✅ Model đã có sẵn
│   └── dao/
│       └── category_dao.py       ✅ Vừa tạo (Bước 1)
└── web/
    └── api/
        ├── categories/           ✅ Vừa tạo
        │   ├── __init__.py       ✅ Bước 5
        │   ├── schema.py         ✅ Bước 2
        │   └── views.py          ✅ Bước 3
        └── router.py             ✅ Updated (Bước 6)
```

---

## 💡 Tips & Best Practices

### **1. Đặt tên theo quy ước**
- File: `snake_case` (ví dụ: `category_dao.py`, `order_item_dao.py`)
- Class: `PascalCase` (ví dụ: `CategoryDAO`, `OrderItemModel`)
- Function: `snake_case` (ví dụ: `get_category_by_id`)

### **2. Async/Await**
- Tất cả methods trong DAO và views đều phải là `async`
- Gọi database phải dùng `await`

### **3. Dependency Injection**
- DAO nhận `session` qua `Depends(get_db_session)`
- Views nhận DAO qua `Depends()`

### **4. Error Handling**
- Dùng `HTTPException` để trả lỗi
- Luôn check `None` trước khi return

### **5. Type Hints**
- Luôn khai báo kiểu trả về: `-> list[Category]`, `-> Category | None`
- Giúp code rõ ràng và IDE autocomplete tốt hơn

---

## 🎯 Thực hành

Bây giờ bạn có thể tự viết CRUD cho các entities khác:

**Dễ**:
- `provinces` - Chỉ có id, name
- `wards` - Có id, name, province_id

**Trung bình**:
- `books` - Nhiều fields (title, author, price, stock...)
- `orders` - Có relationship với users

**Nâng cao**:
- `order_items` - Relationship phức tạp (orders + books)

Hãy bắt đầu với một entity đơn giản và làm theo đúng 5 bước! 🚀
