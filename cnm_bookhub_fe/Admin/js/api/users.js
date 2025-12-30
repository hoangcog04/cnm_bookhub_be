const UsersAPI = {
    getAll: async function () {
        return await API.get("/user/getAllUsers");
    },

    getById: async function (id) {
        return await API.get(`/user/${id}`);
    },

    create: async function (data) {
        return await API.post("/user/register", data);
        // Demo data for Create User (Register):
        // payload: {
        //   "email": "email@example.com",
        //   "password": "password123",
        //   "full_name": "Nguyễn Văn A",
        //   "phone_number": "0912345678",
        //   "role": "user", // "user", "admin"
        // }
    },

    update: async function (id, data) {
        return await API.patch(`/users/${id}`, data);
        // Demo data for Update User:
        // payload: {
        //   "full_name": "Nguyễn Văn B",
        //   "phone_number": "0987654321",
        //   "email": "email@example.com",
        //   "avatar_url": "https://example.com/avatar.jpg",
        //   "province": "TP Hồ Chí Minh",
        //   "role": "user", // "user", "admin"
        //   "ward": "Phường Bến Nghé",
        //   "address": "456 Đường XYZ"
        // }
    },

    // func demo mock postman
    getById1: async function (id) {
        try {
            const list = await this.getAll();
            const users = Array.isArray(list) ? list : (list.data || []);
            const user = users.find(u => u.id == id || u.id === id);
            if (user) return user;
            return await API.get(`/getUserById/${id}`);
        } catch (e) {
            return await API.get(`/getUserById/${id}`);
        }
    },

    delete: async function (id) {
        return await API.delete(`/users/${id}`);
    }
};
