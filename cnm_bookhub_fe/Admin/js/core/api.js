const API = {
  baseURL: "https://c28500f2-d1d8-4ea6-ae8e-cc23a30596e8.mock.pstmn.io",

  async request(endpoint, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) throw new Error(`Lỗi HTTP: ${response.status}`);

      // Kiểm tra Content-Length để tránh lỗi khi body rỗng
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.indexOf("application/json") !== -1) {
        return await response.json();
      } else {
        // Nếu không phải JSON, thử đọc text để debug hoặc return null
        const text = await response.text();
        if (!text) return null; // Body rỗng
        try {
          return JSON.parse(text); // Cố parse lần nữa
        } catch (e) {
          console.warn("API trả về không phải JSON:", text);
          return null; // Return null để phía caller tự xử lý (ví dụ hiện list rỗng)
        }
      }
    } catch (error) {
      console.error("API Error:", error);
      throw error;
    }
  },

  async get(endpoint) {
    return await this.request(endpoint, { method: "GET" });
  },

  async post(endpoint, body) {
    return await this.request(endpoint, {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  async put(endpoint, body) {
    return await this.request(endpoint, {
      method: "PUT",
      body: JSON.stringify(body),
    });
  },

  async delete(endpoint) {
    return await this.request(endpoint, { method: "DELETE" });
  }
};