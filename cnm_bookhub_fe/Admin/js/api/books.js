const BooksAPI = {
  getAllBook: async (limit = 10, offset = 1) => {
    console.log(limit, offset);
    return await API.request(`/book/getAllBooks?limit=${limit}&offset=${offset}`);
    // Demo data for Pagination:
    // Response:
    // {
    //   "items": [
    //      { "id": 1, "title": "Sách A", ... },
    //      { "id": 2, "title": "Sách B", ... }
    //   ],
    //   "totalPage": 5
    // }
  },

  getBookById: async (id) => {
    return await API.request(`/book/getBookById?id=${id}`);
  },

  // Tạo sách mới
  create: async (data) => {
    return await API.request("/book/createBook", {
      method: "POST",
      body: JSON.stringify(data),
    });
    // Demo data for Create Book:
    // payload: {
    //   "title": "Tên sách Demo",
    //   "author": "Tác giả Demo",
    //   "category_id": 1,
    //   "price": 100000,
    //   "available_quantity": 50,
    //   "description": "Mô tả sách...",
    //   "image_url": "https://example.com/image.jpg"
    // }
    // Response:
    // {
    //   "id": 101,
    //   "title": "Tên sách Demo",
    //   "author": "Tác giả Demo",
    //   ...
    // }
  },

  // Cập nhật sách
  update: async (id, data) => {
    return await API.request(`/book/updateBook?id=${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
    // Demo data for Update Book:
    // payload: {
    //   "title": "Tên sách đã sửa",
    //   "price": 120000,
    //   ... (other fields as needed)
    // }
    // Response:
    // {
    //   "id": 101,
    //   "title": "Tên sách đã sửa",
    //   ...
    // }
  },

  // Xóa sách
  delete: async (id) => {
    return await API.request("/book/deleteBook?id=${id}", { method: "DELETE" });
  },
};