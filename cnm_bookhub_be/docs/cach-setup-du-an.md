# Hướng dẫn Setup Dự án

## Yêu cầu hệ thống

- Python >= 3.12
- MySQL 8.4 (hoặc Docker)
- uv (khuyến nghị) hoặc pip

---

## Phương án 1: Code Local + DB Local

### Bước 1: Cài đặt MySQL

Cài đặt MySQL 8.4 trên máy local và tạo database:

```sql
CREATE DATABASE cnm_bookhub_be;
CREATE USER 'cnm_bookhub_be'@'localhost' IDENTIFIED BY 'cnm_bookhub_be';
GRANT ALL PRIVILEGES ON cnm_bookhub_be.* TO 'cnm_bookhub_be'@'localhost';
FLUSH PRIVILEGES;
```

### Bước 2: Setup .env

Copy file `.env.example` thành `.env`:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Chỉnh sửa file `.env`:
- `CNM_BOOKHUB_BE_DB_PORT`: Đổi thành `3306` nếu MySQL local chạy port 3306
- `CNM_BOOKHUB_BE_DB_USER`, `CNM_BOOKHUB_BE_DB_PASS`, `CNM_BOOKHUB_BE_DB_BASE`: Đổi nếu khác với mặc định

### Bước 3: Cài đặt dependencies

**Với uv:**
```bash
uv sync --locked
```

**Với pip:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements-dev.txt
```

### Bước 4: Chạy migrations

```bash
alembic upgrade head
```

### Bước 5: Chạy ứng dụng

**Với uv:**
```bash
uv run -m cnm_bookhub_be
```

**Với pip:**
```bash
python -m cnm_bookhub_be
```

Ứng dụng chạy tại: `http://localhost:8000`
API docs: `http://localhost:8000/api/docs`

---

## Phương án 2: Code Local + DB Docker

### Bước 1: Khởi động MySQL bằng Docker

```bash
docker-compose -f docker-compose.mysql.yml up -d
```

### Bước 2: Setup .env

Copy file `.env.example` thành `.env`:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Chỉnh sửa file `.env` nếu cần:
- `CNM_BOOKHUB_BE_DB_PORT`: Đổi thành `3306` nếu muốn dùng port mặc định của MySQL Docker (mặc định là 3307)
- Các biến khác giữ nguyên nếu dùng cấu hình mặc định

### Bước 3: Cài đặt dependencies

**Với uv:**
```bash
uv sync --locked
```

**Với pip:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements-dev.txt
```

### Bước 4: Chạy migrations

```bash
alembic upgrade head
```

### Bước 5: Chạy ứng dụng

**Với uv:**
```bash
uv run -m cnm_bookhub_be
```

**Với pip:**
```bash
python -m cnm_bookhub_be
```

### Dừng DB khi không dùng:

```bash
docker-compose -f docker-compose.mysql.yml down
```

---

## Phương án 3: Code Full Docker (Development với Auto-reload)

### Bước 1: Setup .env

Copy file `.env.example` thành `.env`:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Chỉnh sửa file `.env` nếu cần (thêm các biến cho Docker nếu muốn):
```bash
CNM_BOOKHUB_BE_VERSION=latest
CNM_BOOKHUB_BE_PORT=8000
```

### Bước 2: Build và chạy với dev config

```bash
docker-compose -f docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up --build
```

Tính năng:
- Auto-reload khi code thay đổi
- Expose port 8000
- Mount code vào container

### Bước 3: Rebuild khi thay đổi dependencies

Nếu sửa `pyproject.toml` hoặc `uv.lock`:

```bash
docker-compose build
```

### Dừng:

```bash
docker-compose down
```

---

## Lưu ý chung

### Tạo migrations mới:

```bash
alembic revision --autogenerate
```

### Chạy migration cụ thể:

```bash
alembic upgrade <revision_id>
```

### Rollback migration:

```bash
alembic downgrade <revision_id>
```

### Seed dữ liệu ban đầu (tùy chọn)

Sau khi chạy migrations, bạn có thể seed dữ liệu mẫu (superuser, category, và 5 quyển sách):

**Với uv:**
```bash
uv run python -m cnm_bookhub_be.db.seed
```

**Với pip:**
```bash
python -m cnm_bookhub_be.db.seed
```

Script sẽ tạo:
- Superuser: `admin@example.com` / `123456`
- Category: "Truyện tranh"
- 5 quyển sách mẫu

**Lưu ý:** Script có thể chạy nhiều lần mà không tạo duplicate (idempotent).

### Environment Variables

- Tất cả biến môi trường phải có prefix `CNM_BOOKHUB_BE_` (trừ `USERS_SECRET`). Xem `cnm_bookhub_be/settings.py` để biết các biến có sẵn.
- File `.env.example` đã chứa các biến cần thiết: `CNM_BOOKHUB_BE_RELOAD`, `CNM_BOOKHUB_BE_DB_HOST`, `CNM_BOOKHUB_BE_DB_PORT`, `USERS_SECRET`

### Troubleshooting

- **Lỗi kết nối DB**: Kiểm tra MySQL đã chạy và thông tin trong `.env` đúng chưa
- **Lỗi migration**: Đảm bảo database đã được tạo trước khi chạy `alembic upgrade head`
- **Port đã được sử dụng**: Đổi `CNM_BOOKHUB_BE_PORT` trong `.env` hoặc dừng service đang dùng port đó

