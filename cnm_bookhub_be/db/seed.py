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
des_6 = """
"Tôi có thể nói rằng Mix là con mèo của Max nhưng tôi cũng có thể tuyên bố rằng Max là con người của Mix." Câu chuyện bắt đầu như thế. Gắn bó với nhau từ thủa thiếu thời, cho tới ngày Mix đã già và bị mù thì Max cũng tình nguyện không xê dịch bất cứ thứ gì trong nhà mình nữa.

Thế nhưng đâu chỉ có chuyện người và mèo làm bạn cùng nhau!  Max còn kết thân với Mex - một con chuột ba hoa lắm lời, còn cùng nhau dọa cho tên trộm sợ chết khiếp, cùng nhau thực hiện những chuyến phiêu lưu trên mái nhà để Mex ngộ ra rằng không phải cứ có cánh mới bay được!
"""
des_7 = """
"Không có ngục tù nào ở bất kỳ thế giới nào mà Tình yêu không thể tìm lối vào. Nếu không hiểu điều này, em không hiểu gì về Tình yêu."

Năm 1895, nhà văn, nhà soạn kịch lừng lẫy Oscar Wilde bị kết án hai năm tù khổ sai vì hành vi đồng tính luyến ái, một tội ở Anh quốc thời bấy giờ. Bỗng chốc mất trắng và trở thành phạm nhân, Wilde đã từ đỉnh cao rơi xuống vực sâu. De Profundis là lá thư Wilde viết trong lúc thụ án, gửi cho người tình cũ của ông là Alfred Douglas. Lá thư dài này vừa là một bản cáo trạng gay gắt về những hành vi của Douglas trong suốt thời gian cả hai bên nhau, vừa là một điếu văn bi ai khi Wilde nuối tiếc những gì mình đã đánh mất, nhưng trên tất cả, nó còn là một hành trình phát triển về mặt tinh thần của chính Wilde sau những tháng ngày khốn khổ.

Và chính trong quãng thời gian tù đày ấy, khi nhìn thấy một phạm nhân chờ xử tử trên sân nhà tù, Wilde đã sáng tác nên Bài ballad về nhà ngục Reading từ chút thông tin ít ỏi có được cùng trí tưởng tượng của người nghệ sĩ. Bằng lòng trắc ẩn của bản thân và những trải nghiệm đau thương thực tế, bài thơ đi từ việc kể lại những ngày cuối đời một tử tù, sang đến miêu tả tình trạng tinh thần của các tù nhân và lên án điều kiện sống khắc nghiệt mà họ phải chịu đựng.

Đôi nét về tác giả Oscar Wilde

Oscar Wilde (1854–1900) là kịch tác gia, tiểu thuyết gia và nhà thơ nổi tiếng người Ireland. Sau khi tốt nghiệp đại học Trinity (1874) và đại học Oxford (1878), ông chuyển tới sống ở thủ đô nước Anh và trở thành một trong những nhà viết kịch được yêu thích nhất London vào đầu thập niên 1890.

Người đời nhớ đến ông qua các câu danh ngôn, các vở kịch, tiểu thuyết Chân dung của Dorian Gray, cũng như những ồn ào xung quanh xu hướng tính dục, việc tù tội và cái chết trẻ của ông.

Các tác phẩm của Oscar Wilde do Nhã Nam xuất bản:
Hoàng tử Hạnh Phúc
Chân dung của Dorian Gray
De Profundis & Bài ballad về nhà ngục Reading
"""
des_8 = """
"Ở mặt nào đó cũng có thể coi gia đình như một chiếc hộp đen. Chẳng ai có thể biết bên trong có gì và cũng khó mà hiểu được nguyên lý của nó."

Những thế giới con tập hợp bảy truyện ngắn khắc họa những lát cắt đa dạng của cuộc sống, được dệt nên từ những niềm vui nhỏ nhoi lẫn nỗi buồn day dứt.

Một người phụ nữ khao khát được làm mẹ đến bất chấp tất cả. Một người bà vô tình gây ra cái chết của cô cháu gái mới mười tháng tuổi. Một người phụ nữ đều đặn viết thư cho tên hung thủ sát hại người thân duy nhất của mình... Những câu chuyện tưởng chừng rời rạc đan cài vào nhau, mở ra một vũ trụ cảm xúc, nơi hy vọng và tuyệt vọng, yêu thương lẫn tổn thương cùng song hành.

Không cường điệu, không phán xét, Ichiho Michi dịu dàng khắc họa những niềm vui, nỗi buồn và tình thương ẩn sâu trong từng "thế giới con" của mỗi người.

Đôi nét về tác giả Ichiho Michi

Ichiho Michi ra mắt văn đàn Nhật Bản vào năm 2007. Với văn phong tinh tế, giàu lòng trắc ẩn và quan niệm "mỗi người đều có những nỗi niềm riêng đáng được trân trọng", các tác phẩm của cô thường khắc họa sâu sắc tâm lý nhân vật, hòa quyện giữa nỗi buồn man mác và sự hài hước nhẹ nhàng.

Cuốn sách Những thế giới con đã mang về cho Ichiho Michi giải Nhà văn mới - giải thưởng văn học Yoshikawa Eiji lần thứ 43, giải Nhà sách tỉnh Shizuoka lần thứ 9, đồng thời giành hạng ba giải Nhà sách Nhật Bản năm 2022.

Các giải thưởng tiêu biểu:

Giải thưởng Văn học Yoshikawa Eiji lần thứ 43 (Những thế giới con).
Giải thưởng Văn học Tình yêu Shimase lần thứ 30 (Ở bên ánh sáng).
Giải thưởng Naoki lần thứ 171 (Đại dịch và tội lỗi).
"""
des_9 = """
Không ai có thể trốn chạy khỏi bóng tối ẩn sâu trong tâm trí mình…

Sophie, một phụ nữ trẻ có cuộc sống êm đềm, bỗng trượt vào vực thẳm của chứng loạn trí. Ban đầu chỉ là những dấu hiệu nhỏ nhặt, những khoảnh khắc lãng quên thoáng qua cùng cảm giác bất an mơ hồ. Thế nhưng, từng chút một, chúng tích tụ lại và trở thành cơn ác mộng không thể kiểm soát.

Sophie có thực sự là kẻ giết người? Có phải chính tay cô đã tàn nhẫn giết hại hàng loạt nạn nhân? Kỳ lạ thay, Sophie chẳng hề nhớ gì về những tội ác đó. Bị nhấn chìm trong nỗi hoài nghi và sợ hãi, Sophie chỉ còn một con đường duy nhất: trốn chạy. Thay tên đổi họ, bắt đầu một cuộc đời mới, tin rằng mình có thể chôn vùi quá khứ vào quên lãng. Nhưng bóng ma của những tội ác chưa rõ thực hư vẫn đeo bám cô không rời. Khi cuộc sống mới vừa bắt đầu cũng là lúc những bí ẩn trong quá khứ dần được vén màn. Liệu Sophie là con quái vật đội lốt người hay chính cô đang phải chạy trốn khỏi kẻ sát nhân thực sự

Giải thưởng/Đề cử

Bộ váy cưới đẫm máu là tiểu thuyết thứ hai của Pierre Lemaitre. Năm 2009, tác phẩm vinh dự đoạt giải thưởng Tiểu thuyết trinh thám Pháp xuất sắc nhất (prix du Meilleur polar francophone).

Vài nét về tác giả Pierre Lemaitre

Pierre Lemaitre sinh ngày 19 tháng Tư năm 1951 tại Paris. Ông từng dạy học cho người lớn nhiều năm, chủ yếu là về văn học Pháp, văn học Mỹ, phân tích văn học và văn hóa nói chung.
Đến năm 2006, ông chuyển sang viết văn và kịch bản. Các tác phẩm của ông đã được dịch ra hơn ba mươi thứ tiếng, được chuyển thể thành phim và giúp ông giành nhiều giải thưởng.
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
                    full_name="Quản trị viên",
                    is_superuser=True,
                    is_verified=True,
                    is_active=True,
                    role="ADMIN",
                    address_detail="123 Võ Văn Kiệt",
                    phone_number="0909090909",
                    ward_code="10003",
                )
                session.add(superuser)
                await session.flush()
                print(f"Superuser created: {superuser.email} with password 123456")

            # 1.5 create 5 users
            print("Creating 5 users...")
            users_full_names = [
                "Nguyễn Văn An",
                "Trần Thị Bình",
                "Lê Văn Cường",
                "Phạm Thị Dung",
                "Hoàng Văn Em",
            ]
            for i in range(5):
                email = f"user{i + 1}@example.com"
                # Check if user already exists
                result = await session.execute(
                    select(User).where(User.email == email)  # type: ignore
                )
                existing_user = result.unique().scalar_one_or_none()

                if existing_user:
                    print(f"User '{email}' already exists, skipping...")
                else:
                    user = User(
                        email=email,
                        hashed_password=password_helper.hash("123456"),
                        full_name=users_full_names[i],
                        is_superuser=False,
                        is_verified=True,
                        is_active=True,
                        role="USER",
                        address_detail="123 Võ Văn Kiệt",
                        phone_number="0909090909",
                        ward_code="10003",
                    )
                    session.add(user)
                    await session.flush()
                    print(f"User created: {user.email} ({user.full_name})")

            # 2. Create categories
            print("Creating categories...")
            categories_data = [
                {"name": "Truyện tranh"},
                {"name": "Văn học thiếu nhi"},
                {"name": "Văn học kinh điển"},
                {"name": "Văn học Nhật Bản"},
                {"name": "Trinh thám"},
            ]

            categories_dict = {}
            for cat_data in categories_data:
                result = await session.execute(
                    select(Category).where(Category.name == cat_data["name"])
                )
                existing_category = result.scalar_one_or_none()

                if existing_category:
                    categories_dict[cat_data["name"]] = existing_category
                    print(
                        f"Category '{cat_data['name']}' already exists, using existing..."
                    )
                else:
                    category = Category(name=cat_data["name"])
                    session.add(category)
                    await session.flush()
                    categories_dict[cat_data["name"]] = category
                    print(f"Category created: {category.name}")

            # 3. Create books
            print("Creating books...")
            books_data = [
                {
                    "title": "12 THÚ CƯNG GIÁNG SINH",
                    "author": "Anne Sawan;Judi Abbot",
                    "price": 50000,
                    "stock": 100,
                    "image_urls": "https://bizweb.dktcdn.net/thumb/large/100/363/455/products/12-thu-cung-giang-sinh-01.jpg?v=1734613539847,",
                    "description": des_1,
                    "category_id": categories_dict["Truyện tranh"].id,
                },
                {
                    "title": "LÁ THƯ",
                    "author": "Richard Paul Evans",
                    "price": 45000,
                    "stock": 80,
                    "image_urls": "https://bizweb.dktcdn.net/thumb/large/100/363/455/products/lathue1704163860519.jpg?v=1705552507860,",
                    "description": des_2,
                    "category_id": categories_dict["Truyện tranh"].id,
                },
                {
                    "title": "MỖI NGÀY ĐỀU LÀ GIÁNG SINH",
                    "author": "Sung-Kyung Park",
                    "price": 55000,
                    "stock": 90,
                    "image_urls": "https://bizweb.dktcdn.net/thumb/large/100/363/455/products/moingaydeulagiangsinhe17026249.jpg?v=1705552509227,",
                    "description": des_3,
                    "category_id": categories_dict["Truyện tranh"].id,
                },
                {
                    "title": "ĐỒNG HỒ",
                    "author": "Richard Paul Evans",
                    "price": 40000,
                    "stock": 70,
                    "image_urls": "https://bizweb.dktcdn.net/thumb/large/100/363/455/products/donghoe1702267085893.jpg?v=1705552510170,",
                    "description": des_4,
                    "category_id": categories_dict["Truyện tranh"].id,
                },
                {
                    "title": "CHIẾC HỘP GIÁNG SINH",
                    "author": "Richard Paul Evans",
                    "price": 48000,
                    "stock": 85,
                    "image_urls": "https://bizweb.dktcdn.net/thumb/1024x1024/100/363/455/products/chiechopgiangsinhe170226706527.jpg?v=1705552510273,",
                    "description": des_5,
                    "category_id": categories_dict["Truyện tranh"].id,
                },
                {
                    "title": "Chuyện con mèo và con chuột bạn thân của nó (TB 2026)",
                    "author": "Luis Sepúlveda",
                    "price": 44200,
                    "stock": 75,
                    "image_urls": "https://bizweb.dktcdn.net/thumb/large/100/363/455/products/chuyenconmeoconchuotbanthancua-1d21bba5-7c5d-4e3f-8768-7d531a104237.jpg?v=1767840646770,",
                    "description": des_6,
                    "category_id": categories_dict["Văn học thiếu nhi"].id,
                },
                {
                    "title": "De Profundis & Bài ballad về nhà ngục Reading",
                    "author": "Oscar Wilde",
                    "price": 93500,
                    "stock": 60,
                    "image_urls": "https://bizweb.dktcdn.net/thumb/large/100/363/455/products/bai-ballad-ve-nha-nguc-reasing.png?v=1767762734500,",
                    "description": des_7,
                    "category_id": categories_dict["Văn học kinh điển"].id,
                },
                {
                    "title": "Những thế giới con",
                    "author": "Ichiho Michi",
                    "price": 148750,
                    "stock": 50,
                    "image_urls": "https://bizweb.dktcdn.net/thumb/large/100/363/455/products/nhung-the-gioi-con.png?v=1767759622190,",
                    "description": des_8,
                    "category_id": categories_dict["Văn học Nhật Bản"].id,
                },
                {
                    "title": "Bộ váy cưới đẫm máu",
                    "author": "Pierre Lemaitre",
                    "price": 169150,
                    "stock": 65,
                    "image_urls": "https://bizweb.dktcdn.net/thumb/large/100/363/455/products/bo-vay-cuoi-dam-mau.png?v=1767756324167,",
                    "description": des_9,
                    "category_id": categories_dict["Trinh thám"].id,
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
            print(f"   - Categories: {', '.join(categories_dict.keys())}")
            print(f"   - Books created: {created_count}/{len(books_data)}")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error seeding data: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_data())
