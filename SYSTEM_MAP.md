# System Architecture Map (CNM BookHub)

Dưới đây là sơ đồ kết nối và các cổng (Port) chi tiết trong hệ thống của bạn để bạn dễ dàng quản lý và sử dụng MySQL Workbench.

## 1. Bản đồ các cổng kết nối (Port Map)

| Thành phần | Cổng (Port) | Địa chỉ truy cập | Ghi chú |
| :--- | :--- | :--- | :--- |
| **Backend (FastAPI)** | `8000` | `http://localhost:8000/api/docs` | Nơi xử lý logic và API. |
| **Frontend (App)** | `8080` | `http://localhost:8080/Client/index.html` | Giao diện người dùng. |
| **MySQL (trong Docker)** | `3306` | *Nội bộ Docker* | Cổng mặc định bên trong container. |
| **MySQL (Mở ra máy thật)**| `3309` | `localhost:3309` | **Dùng cổng này để kết nối Workbench.** |
| **Mailpit (Email Test)** | `8025` | `http://localhost:8025` | Giao diện xem email gửi đi từ hệ thống. |

---

## 2. Cách kết nối MySQL Workbench vào Docker

Để xem dữ liệu bên trong Docker bằng Workbench, bạn hãy tạo một **Connection** mới với thông tin sau:

- **Hostname**: `127.0.0.1` hoặc `localhost`
- **Port**: `3306` (Đây là cổng tiêu chuẩn kết nối vào Docker)
- **Username**: `cnm_bookhub_be` (hoặc `root`)
- **Password**: `cnm_bookhub_be` (nếu dùng user trên) hoặc `cnm_bookhub_be` (cho root)
- **Default Schema**: `cnm_bookhub_be`

---

## 3. Luồng dữ liệu hoạt động

1. **Khi bạn thao tác trên Frontend**:
   - Frontend gửi yêu cầu đến Backend (cổng `8000`).
2. **Backend xử lý**:
   - Backend kết nối vào MySQL Server (đang chạy trong Docker) thông qua địa chỉ `localhost:3306`.
3. **Khi bạn dùng Workbench**:
   - Workbench kết nối trực tiếp vào `localhost:3306` để hiển thị dữ liệu cho bạn thấy.

---

## 4. Cập nhật mã nguồn (.env)

Để Backend luôn kết nối đúng vào cổng 3309, hãy đảm bảo file `.env` của bạn có dòng:
```env
CNM_BOOKHUB_BE_DB_PORT=3306
CNM_BOOKHUB_BE_DB_HOST=localhost
CNM_BOOKHUB_BE_DB_USER=cnm_bookhub_be
CNM_BOOKHUB_BE_DB_PASS=cnm_bookhub_be
CNM_BOOKHUB_BE_DB_BASE=cnm_bookhub_be
```
