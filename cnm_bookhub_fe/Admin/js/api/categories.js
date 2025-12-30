const CategoriesAPI = {
  getCategoryName: async () => {
    return await API.request("/category/getcategoryName");
    // Demo data:
    // [
    //   {
    //     "id": 1,
    //     "name": "Thơ - Kịch"
    //   },
    //   {
    //     "id": 2,
    //     "name": "Kinh doanh"
    //   }
    // ]
  },

  getAllCategory: async () => {
    return await API.request("/category/getAllCategory");
    // Phần này không cần phân trang vì số danh mục sách không quá lớn
    // Demo data:
    // [
    //   {
    //     "id": 1,
    //     "name": "Thơ - Kịch",
    //     "number_of_books": 12,
    //     "deleted_at": null
    //   },
    //   {
    //     "id": 2,
    //     "name": "Kinh doanh",
    //     "number_of_books": 8,
    //     "deleted_at": "2024-12-01T10:15:30Z"
    //   }
    // ]
  },

  getCategoryDetail: async (id) => {
    return await API.request(`/category/${id}`);

    // Demo data:
    // {
    //   "category": {
    //     "id": 1,
    //       "name": "Thơ - Kịch"
    //   },
    //   "books": [
    //     {
    //       "id": "book-tho-001",
    //       "title": "Thơ Xuân Diệu",
    //       "image_url":
    //         "https://bizweb.dktcdn.net/thumb/large/100/363/455/products/z7233398059560-274012ae3afdd24839e69d64afd793b0.jpg?v=1763368809590"
    //     },
    //     {
    //       "id": "book-tho-002",
    //       "title": "Kịch nói Việt Nam hiện đại",
    //       "image_url":
    //         "https://bizweb.dktcdn.net/thumb/large/100/363/455/products/z7233398059560-274012ae3afdd24839e69d64afd793b0.jpg?v=1763368809590"
    //     },
    //     {
    //       "id": "book-tho-003",
    //       "title": "Thơ tình lãng mạn",
    //       "image_url":
    //         "https://bizweb.dktcdn.net/thumb/large/100/363/455/products/z7233398059560-274012ae3afdd24839e69d64afd793b0.jpg?v=1763368809590"
    //     }
    //   ]
    // }
  },

  create: async (data) => {
    return await API.request("/category", {
      method: "POST",
      body: JSON.stringify(data),
    });
    // Demo data for Create Category:
    // payload: {
    //   "name": "Tên danh mục mới",
    // }
    // Response:
    // {
    //   "id": 12,
    //   "name": "Tên danh mục mới",
    //   "number_of_books": 0,
    //   "deleted_at": null
    // }
  },

  update: async (id, data) => {
    return await API.request(`/category/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
    // Demo data for Update Category:
    // payload: {
    //   "name": "Tên danh mục đã sửa",
    // }
    // Response:
    // {
    //   "id": 12,
    //   "name": "Tên danh mục đã sửa",
    //   "number_of_books": 5,
    //   "deleted_at": null
    // }
  },

  delete: async (id) => {
    return await API.request(`/category/${id}`, { method: "DELETE" });
  },
};

