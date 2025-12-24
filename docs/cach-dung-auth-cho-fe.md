# Hướng dẫn sử dụng Authentication cho Frontend

Backend sử dụng **FastAPI Users** với **JWT authentication**. Tất cả API có prefix `/api`.

## 📋 Tổng quan

- **Đăng ký**: Dùng `email` và `password` (JSON)
- **Đăng nhập**: Dùng `username` (giá trị là email) và `password` (Form Data)
- **Token**: JWT token không có thời gian hết hạn
- **Header**: Gửi token trong header `Authorization: Bearer <token>`

## 🔐 Các Endpoint Authentication

### 1. Đăng ký tài khoản
```
POST /api/auth/register
Content-Type: application/json

Body:
{
  "email": "user@example.com",
  "password": "password123"
}
```

### 2. Đăng nhập (Lấy JWT Token)
```
POST /api/auth/jwt/login
Content-Type: application/x-www-form-urlencoded

Body (form data):
username=user@example.com&password=password123
```

**⚠️ Lưu ý quan trọng:**
- Phải gửi dưới dạng **form data** (`application/x-www-form-urlencoded`), không phải JSON
- Field tên là `username` nhưng giá trị là **email** của bạn
- Đây là cách hoạt động của FastAPI Users theo chuẩn OAuth2

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### 3. Đăng xuất
**⚠️ Lưu ý:** Với JWT Bearer authentication, logout endpoint có thể không hoạt động vì JWT là stateless. Để logout, bạn chỉ cần xóa token ở client side.

```javascript
// Logout bằng cách xóa token
const logout = () => {
  localStorage.removeItem('token');
  // Redirect về trang login
};
```

Nếu muốn gọi logout endpoint (có thể không hoạt động):
```
POST /api/auth/jwt/logout
Authorization: Bearer <token>
```

### 4. Reset password
```
POST /api/auth/forgot-password
Content-Type: application/json

Body:
{
  "email": "user@example.com"
}
```

### 5. Verify email
```
POST /api/auth/verify
Content-Type: application/json

Body:
{
  "token": "<verification_token>"
}
```

## 👤 User Endpoints (Cần token)

### Lấy thông tin user hiện tại
```
GET /api/users/me
Authorization: Bearer <token>
```

### Cập nhật thông tin user
```
PATCH /api/users/me
Authorization: Bearer <token>
Content-Type: application/json

Body:
{
  "email": "newemail@example.com",
  "full_name": "Tên mới"
}
```

## 💻 Ví dụ code JavaScript/TypeScript

### 1. Đăng ký
```javascript
const register = async (email, password) => {
  const response = await fetch('http://localhost:8000/api/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: email,
      password: password,
    }),
  });
  
  return await response.json();
};
```

### 2. Đăng nhập
```javascript
const login = async (email, password) => {
  // Tạo form data
  const formData = new URLSearchParams();
  formData.append('username', email); // ⚠️ Dùng 'username' nhưng giá trị là email
  formData.append('password', password);

  const response = await fetch('http://localhost:8000/api/auth/jwt/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });

  const data = await response.json();
  
  // Lưu token vào localStorage
  if (data.access_token) {
    localStorage.setItem('token', data.access_token);
  }
  
  return data;
};
```

### 3. Gọi API protected (có token)
```javascript
const getCurrentUser = async () => {
  const token = localStorage.getItem('token');
  
  const response = await fetch('http://localhost:8000/api/users/me', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  return await response.json();
};
```

### 4. Axios example (nếu dùng Axios)
```javascript
import axios from 'axios';

// Setup axios instance với base URL
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// Thêm token vào mọi request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Đăng nhập
const login = async (email, password) => {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  
  const response = await api.post('/auth/jwt/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  
  if (response.data.access_token) {
    localStorage.setItem('token', response.data.access_token);
  }
  
  return response.data;
};

// Lấy thông tin user
const getCurrentUser = async () => {
  const response = await api.get('/users/me');
  return response.data;
};
```

## 📝 Lưu ý

1. **Email vs Username**: 
   - Đăng ký dùng `email`
   - Đăng nhập dùng `username` nhưng giá trị là email
   - Đây là cách hoạt động của FastAPI Users theo chuẩn OAuth2

2. **Token Storage**: 
   - Nên lưu token vào `localStorage` hoặc `sessionStorage`
   - Hoặc dùng httpOnly cookie (cần config thêm ở backend)

3. **Error Handling**: 
   - Kiểm tra `response.ok` hoặc `response.status` trước khi parse JSON
   - Xử lý lỗi 401 (Unauthorized) để redirect về trang login

4. **Swagger Docs**: 
   - Xem chi tiết API tại: `http://localhost:8000/api/docs`
   - Test trực tiếp các endpoint tại đây

5. **Logout**: 
   - Với JWT Bearer token, logout chủ yếu là xóa token ở client side
   - Token không thể bị "vô hiệu hóa" vì JWT là stateless
   - Để bảo mật hơn, có thể implement token blacklist ở backend

