"""Seed script to populate initial data."""

import asyncio

from fastapi_users.password import PasswordHelper
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from cnm_bookhub_be.db.models import load_all_models
from cnm_bookhub_be.db.models.books import Book
from cnm_bookhub_be.db.models.categories import Category
from cnm_bookhub_be.db.models.users import User
from cnm_bookhub_be.settings import settings

des_1 = """
Với minh họa rực rỡ đáng yêu, 12 thú cưng Giáng sinh kể chuyện một bé gái nhận được món
quà Giáng sinh đặc biệt: mỗi ngày một loài thú cưng khác nhau như mèo, ếch, gà, sư tử,
gấu... do những người thân yêu của em gửi tặng. Vào ngày thứ 12 của mùa Giáng sinh, em
được Ông Già Noel tặng 12 chú tuần lộc biết bay. Sách dạy trẻ tập đếm, học về loài vật,
tên gọi các thành viên trong gia đình và những đặc trưng của Giáng sinh qua trò chơi ghi
nhớ thú vị. Một món quà Giáng sinh dễ thương và ý nghĩa dành cho bạn nhỏ 2+ yêu động vật
cũng như độc giả mọi lứa tuổi yêu thú cưng.
"""
des_2 = """
Hai chục năm sau cái chết của cô con gái độc nhất Andrea, David vẫn khép chặt trái tim
mìnhvới nỗi đau và với cả người vợ, MaryAnne. Bức thư bí ẩn đặt trênmộ con gái, ở vào
thời điểm tưởng như kết thúc một chuyện tình không được chăm bón, lại mở ra những lối đi
không ngờ. Lá thư là hành trình tìm kiếm bản thân của David, là nỗ lực tự giải thoát
khỏi nỗi đau dai dẳng của tuổi thơ bị ruồng bỏ và tuổi trưởng thành đầy mất mát. Lá thư
là chuyện tình của David và MaryAnne, nhưng đồng thời cũng là câu chuyện về tình yêu của
tất cả chúng ta, về những dông bão phải đương đầu khi giai đoạn hạnh phúc lâng lâng của
một mối quan hệ dần hạ cánh thành những thử thách khắc nghiệt của hiện thực. Câu chuyện
mầu nhiệm trong tác phẩm đã thành kinh điển mùa lễ, Chiếc hộp Giáng sinh, giờ đây đã trở
nên trọn vẹn với cuốn cuối cùng: Lá thư. Đừng đọc nếu bạn cần một cuốn sách khiến trái
tim reo vui. Nhưng hãy đọc nếu bạn muốn nhìn sâu vào trong chính mình, nhìn vượt ra
ngoàibản thân.Hãy đọc nếu bạn muốn ánh sáng của nó soi rọi đến những chốn tối tăm nhất
trong tim.
"""
des_3 = """
Vào sinh nhật và cũng là Giáng sinh năm 15 tuổi, cô bé Kyung bàng hoàng khi phải đối
diên với hàng loạt những tin sét đánh ngang tai: bố mẹ chuẩn bị ly hôn, bạn thân nhất
đòi tuyệt giao, ông nội dọn tới viện dưỡng lão không một lời từ biệt, anh trai chị gái
chẳng ai thiết tha ở lại nhà.
"""
des_4 = """
Những dòng nhật ký đầy dự cảm của David Parkin đưa ta quay ngược đồng hồ trở về nước Mỹ
những năm đầu thế kỷ hai mươi, lần theo cuộc đời của David và MaryAnne khi họ tìm thấy
nhau, trải qua thăng hoa ngây ngất lẫn tuyệt vọng tận cùng, để rồi khám phá ra sức mạnh
của lòng trung thành, sự khoan thứ. Và vượt trên tất cả là tình yêu, là sự tử tế còn
sống mãi, dù đôi khi tưởng như rung rinh sắp tắt lụi bởi kẹt giữa cám dỗ và hoài nghi.
"""
des_5 = """
Giáng sinh đã về trên thành phố. Những cơn gió tháng Mười hai buốt giá, tuyết rơi dày
và ngọn lửa trong lò sưởi đã rực lên ấm nóng. Trong căn áp mái một ngôi biệt thự trên
khu Đại Lộ thành phố Salt Lake, những bức thư ngả vàng nằm đó mấy chục năm, chờ được
đọc lên lần nữa. Những lá thư bí ẩn khiến người ta rơi lệ, bởi nỗi đau song hành cùng
tình yêu tha thiết của một người mẹ mất con. Và nhờ đó, ý nghĩa của Chiếc hộp Giáng Sinh
đựng những bức thư, của ngày Giáng sinh thiêng liêng đã được hé lộ. Một cuốn sách như
lời ngợi ca tình yêu bất tử mà Thượng đế dành cho loài người, khi Người gửi con trai
mình ra đi, dẫu biết con đường nào chờ đợi phía trước...
"""


async def seed_data() -> None:  # noqa: PLR0915
    """Seed initial data into database."""
    # Load all models first
    load_all_models()

    # Create engine and session
    engine = create_async_engine(str(settings.db_url), echo=False)
    async_session = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    async with async_session() as session:
        try:
            # 1. Create superuser
            print("Creating superuser...")
            password_helper = PasswordHelper()

            # Check if user already exists
            result = await session.execute(
                select(User).where(User.email == "admin@example.com")  # type: ignore
            )
            existing_user = result.unique().scalar_one_or_none()

            if existing_user:
                print("Superuser already exists, skipping...")
            else:
                hashed_password = password_helper.hash("123456")
                superuser = User(
                    email="admin@example.com",
                    hashed_password=hashed_password,
                    is_superuser=True,
                    is_verified=True,
                    is_active=True,
                    address_detail="123 Võ Văn Kiệt",
                    phone_number="0909090909",
                    ward_code="10003",
                )
                session.add(superuser)
                await session.flush()
                print(f"Superuser created: {superuser.email} with password 123456")

            # 1.5 create 5 users
            print("Creating 5 users...")
            for i in range(5):
                user = User(
                    email=f"user{i + 1}@example.com",
                    hashed_password=password_helper.hash("123456"),
                    is_superuser=False,
                    is_verified=True,
                    is_active=True,
                    address_detail="123 Võ Văn Kiệt",
                    phone_number="0909090909",
                    ward_code="10003",
                )
                session.add(user)
                await session.flush()
                print(f"User created: {user.email}")

            # 2. Create category "Truyện tranh"
            print("Creating category...")
            result = await session.execute(
                select(Category).where(Category.name == "Truyện tranh")
            )
            existing_category = result.scalar_one_or_none()

            if existing_category:
                category = existing_category
                print("Category already exists, using existing...")
            else:
                category = Category(name="Truyện tranh")
                session.add(category)
                await session.flush()
                print(f"Category created: {category.name}")

            # 3. Create books
            print("Creating books...")
            books_data = [
                {
                    "title": "12 THÚ CƯNG GIÁNG SINH",
                    "author": "Anne Sawan;Judi Abbot",
                    "price": 50000.0,
                    "stock": 100,
                    "image_urls": "https://bizweb.dktcdn.net/thumb/large/100/363/455/products/12-thu-cung-giang-sinh-01.jpg?v=1734613539847,",
                    "description": des_1,
                    "category_id": category.id,
                },
                {
                    "title": "LÁ THƯ",
                    "author": "Richard Paul Evans",
                    "price": 45000.0,
                    "stock": 80,
                    "image_urls": "https://bizweb.dktcdn.net/thumb/large/100/363/455/products/lathue1704163860519.jpg?v=1705552507860,",
                    "description": des_2,
                    "category_id": category.id,
                },
                {
                    "title": "MỖI NGÀY ĐỀU LÀ GIÁNG SINH",
                    "author": "Sung-Kyung Park",
                    "price": 55000.0,
                    "stock": 90,
                    "image_urls": "https://bizweb.dktcdn.net/thumb/large/100/363/455/products/moingaydeulagiangsinhe17026249.jpg?v=1705552509227,",
                    "description": des_3,
                    "category_id": category.id,
                },
                {
                    "title": "ĐỒNG HỒ",
                    "author": "Richard Paul Evans",
                    "price": 40000.0,
                    "stock": 70,
                    "image_urls": "https://bizweb.dktcdn.net/thumb/large/100/363/455/products/donghoe1702267085893.jpg?v=1705552510170,",
                    "description": des_4,
                    "category_id": category.id,
                },
                {
                    "title": "CHIẾC HỘP GIÁNG SINH",
                    "author": "Richard Paul Evans",
                    "price": 48000.0,
                    "stock": 85,
                    "image_urls": "https://bizweb.dktcdn.net/thumb/1024x1024/100/363/455/products/chiechopgiangsinhe170226706527.jpg?v=1705552510273,",
                    "description": des_5,
                    "category_id": category.id,
                },
            ]

            created_count = 0
            for book_data in books_data:
                # Check if book already exists
                result = await session.execute(
                    select(Book).where(Book.title == book_data["title"])
                )
                existing_book = result.scalar_one_or_none()

                if existing_book:
                    print(f"Book '{book_data['title']}' already exists, skipping...")
                    continue

                book = Book(**book_data)
                session.add(book)
                created_count += 1
                print(f"Book created: {book.title}")

            await session.commit()
            print("\n✅ Seed completed successfully!")
            print("   - Superuser: admin@example.com / password123")
            print("   - Category: Truyện tranh")
            print(f"   - Books created: {created_count}/5")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error seeding data: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_data())
