const OrdersPage = {
  render: async () => {
    const pageBody = document.getElementById("page-body")
    Layout.setPageTitle("Quản lý đơn hàng")
    pageBody.innerHTML = `
            <div class="page-header">
                <h1 class="page-title">Quản lý đơn hàng</h1>
                <p class="page-subtitle">Xem và xử lý các đơn hàng từ khách hàng</p>
            </div>
            <div class="card" style="padding: 40px; text-align: center;">
                <p style="font-size: 18px; color: #6b7280;">Trang quản lý đơn hàng đang được phát triển...</p>
            </div>
        `
  },
}
