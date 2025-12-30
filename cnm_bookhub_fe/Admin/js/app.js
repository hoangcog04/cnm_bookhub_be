document.addEventListener("DOMContentLoaded", async () => {
  try {
    // ⏳ ĐỢI LAYOUT XONG
    await Layout.init()

    Router.register("books", () => BooksPage.render())
    Router.register("book-detail", () => BookDetailPage.render())
    Router.register("book-form", () => BookFormPage.render())
    Router.register("categories", () => CategoriesPage.render())
    Router.register("categories/categoryDetail", () => CategoryFormPage.render())
    Router.register("category-form", () => CategoryFormPage.render())
    Router.register("users", () => UsersPage.render())
    // Route for User Detail/Form
    Router.register("users/detail", () => UserFormPage.render())

    Router.init()
  } catch (err) {
    console.error("Init app failed:", err)
  }
})
