const UserFormPage = {
    userId: null,

    render: async function () {
        try {
            await ScriptLoader.load("js/api/users.js");
            await Layout.renderBody("pages/user_form.html");

            // Get ID from URL Query Params
            const queryId = Router.queryParams && Router.queryParams.id;
            this.userId = queryId || null;

            if (this.userId) {
                Layout.setPageTitle("Cập nhật người dùng");
                document.getElementById("user-form-title").textContent = "Cập nhật tài khoản";
                this.loadUserDetail(this.userId);
                this.setupBackButton("Quay lại danh sách", "users");
            } else {
                Layout.setPageTitle("Thêm người dùng mới");
                document.getElementById("user-form-title").textContent = "Thêm người dùng mới";
                this.setupBackButton("Quay lại danh sách", "users");
                // Reset form or set defaults
                document.getElementById("user-avatar-preview").src = "https://ui-avatars.com/api/?name=New+User&background=random";
            }

            this.attachEventListeners();
        } catch (error) {
            console.error("Error rendering user form:", error);
        }
    },

    setupBackButton: function (text, route) {
        const backBtn = document.getElementById("btn-back-user");
        const backText = document.getElementById("btn-back-user-text");
        if (backBtn && backText) {
            backText.textContent = text;
            backBtn.onclick = () => Router.navigate(route);
        }
    },

    loadUserDetail: async function (id) {
        try {
            const user = await UsersAPI.getById(id);
            // Assuming user is object or { data: ... }
            const userData = user.data || user;

            if (!userData || !userData.id) {
                Utils.showToast("error", "Không tìm thấy người dùng!");
                Router.navigate("users");
                return;
            }

            // 1. Populate Main Inputs
            document.getElementById("user-name").value = userData.full_name || "";
            document.getElementById("user-email").value = userData.email || "";
            document.getElementById("user-phone").value = userData.phone_number || "";
            document.getElementById("user-role").value = (userData.role || "user").toLowerCase();
            document.getElementById("user-address").value = userData.address_detail || "";

            if (document.getElementById("user-avatar-url")) {
                document.getElementById("user-avatar-url").value = userData.avatar_url || "";
            }

            // 2. Populate Ward/Province Split (ComboBoxes)
            // Function to add option if not exists
            const addOption = (selectId, value, text) => {
                const select = document.getElementById(selectId);
                if (select && value) {
                    const opt = document.createElement("option");
                    opt.value = value;
                    opt.text = text;
                    opt.selected = true;
                    select.add(opt);
                }
            };

            if (userData.ward) {
                if (userData.ward.province) {
                    addOption("user-province", userData.ward.province.code || "UNKNOWN", userData.ward.province.full_name);
                }
                addOption("user-ward", userData.ward.code || "UNKNOWN", userData.ward.full_name);
            }

            // 3. Populate Sidebar Profile
            if (document.getElementById("profile-name-display"))
                document.getElementById("profile-name-display").textContent = userData.full_name || "User";

            if (document.getElementById("profile-email-display"))
                document.getElementById("profile-email-display").textContent = userData.email || "";

            if (document.getElementById("profile-id-display"))
                document.getElementById("profile-id-display").textContent = userData.id ? "#" + userData.id.slice(-4).toUpperCase() : "#---";

            if (document.getElementById("profile-join-date"))
                document.getElementById("profile-join-date").textContent = userData.created_at ? new Date(userData.created_at).toLocaleDateString('vi-VN') : "---";

            // Status Badge
            const statusBadge = document.getElementById("profile-status-badge");
            if (statusBadge) {
                if (userData.is_active) {
                    statusBadge.textContent = "Hoạt động";
                    statusBadge.className = "status-badge status-active";
                } else {
                    statusBadge.textContent = "Ngưng hoạt động";
                    statusBadge.className = "status-badge status-inactive";
                }
            }

            // Avatar Preview
            const avatarSrc = userData.avatar_url || `https://ui-avatars.com/api/?name=${userData.full_name || 'User'}&background=random`;
            document.getElementById("user-avatar-preview").src = avatarSrc;

            // Handle Avatar URL Input Change for Preview
            const urlInput = document.getElementById("user-avatar-url");
            if (urlInput) {
                urlInput.addEventListener("input", (e) => {
                    if (e.target.value) document.getElementById("user-avatar-preview").src = e.target.value;
                });
            }

        } catch (error) {
            console.error("Error loading user detail:", error);
            Utils.showToast("error", "Lỗi khi tải thông tin người dùng");
            Router.navigate("users");
        }
    },

    attachEventListeners: function () {
        // Edit Button
        const btnEdit = document.getElementById("btn-edit-user");
        if (btnEdit) btnEdit.onclick = () => this.toggleEditMode(true);

        // Cancel Button
        const btnCancel = document.getElementById("btn-cancel-user");
        if (btnCancel) btnCancel.onclick = () => {
            // Re-load data to revert changes
            if (this.userId) this.loadUserDetail(this.userId);
            this.toggleEditMode(false);
        };

        // Save Button
        document.getElementById("btn-save-user").onclick = () => this.saveUser();

        // Avatar change preview (simple local preview)
        const fileInput = document.getElementById("user-avatar-input");
        if (fileInput) {
            fileInput.addEventListener("change", (e) => {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        document.getElementById("user-avatar-preview").src = e.target.result;
                    }
                    reader.readAsDataURL(file);
                }
            });
        }
    },

    toggleEditMode: function (isEdit) {
        const inputs = document.querySelectorAll(".form-control-modern");
        inputs.forEach(input => input.disabled = !isEdit);

        // Toggle Buttons
        const viewActions = document.getElementById("view-actions");
        const editActions = document.getElementById("edit-actions");
        const avatarEditBtn = document.getElementById("btn-change-avatar");

        if (isEdit) {
            viewActions.style.display = "none";
            editActions.style.display = "flex";
            if (avatarEditBtn) avatarEditBtn.style.display = "flex";
        } else {
            viewActions.style.display = "flex";
            editActions.style.display = "none";
            if (avatarEditBtn) avatarEditBtn.style.display = "none";
        }
    },

    saveUser: async function () {
        const name = document.getElementById("user-name").value;
        const email = document.getElementById("user-email").value;
        const phone = document.getElementById("user-phone").value;
        const role = document.getElementById("user-role").value;
        // const password = document.getElementById("user-password").value; // Removed from UI as requested? Or keep separate?
        // Assuming password reset is separate flow now based on sidebar button.

        if (!name || !email) {
            Utils.showToast("warning", "Vui lòng nhập tên và email");
            return;
        }

        const data = {
            full_name: name,
            email,
            phone_number: phone,
            role,
            // Map other fields...
            avatar_url: document.getElementById("user-avatar-url").value,
            address_detail: document.getElementById("user-address").value,
            // Ward/Province logic would go here
        };

        try {
            if (this.userId) {
                await UsersAPI.update(this.userId, data);
                Utils.showToast("success", "Cập nhật thành công!");
                this.toggleEditMode(false); // Return to view mode
            } else {
                await UsersAPI.create(data);
                Utils.showToast("success", "Thêm mới thành công!");
                Router.navigate("users");
            }
            // Router.navigate("users"); // Don't navigate away on edit save, just stay
        } catch (error) {
            console.error("Error saving user:", error);
            Utils.showToast("error", "Có lỗi xảy ra khi lưu dữ liệu");
        }
    }
};
