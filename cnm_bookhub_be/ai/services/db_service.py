from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Không tìm thấy biến 'DATABASE_URL' trong file .env")

engine = create_engine(DATABASE_URL)

def get_all_books_from_mysql():
    formatted_books = []
    
    with engine.connect() as connection:
        query = text("""
            SELECT 
                b.id, 
                b.title, 
                b.author, 
                b.price,
                b.stock,
                b.description, 
                b.image_urls,
                c.name as category_name
            FROM books b
            JOIN categories c ON b.category_id = c.id
            WHERE stock > 0 AND b.deleted = 0
        """)
        
        result = connection.execute(query)
        keys = result.keys()
        
        for row in result:
            row_dict = dict(zip(keys, row))
            
            book = {
                "id": str(row_dict['id']),
                "title": row_dict['title'],
                "author": row_dict['author'],
                "price": int(row_dict['price']),
                "category": row_dict['category_name'], 
                "description": row_dict['description'],
                "image_url": row_dict['image_urls']
            }
            formatted_books.append(book)
            
    return formatted_books

def get_unique_categories():
    """Lấy danh sách tên các danh mục đang có trong DB"""
    categories = []
    try:
        with engine.connect() as connection:
            query = text("SELECT DISTINCT name FROM categories") 
            result = connection.execute(query)
            for row in result:
                if row[0]: # row[0] là cột name
                    categories.append(row[0])
        return categories
    except Exception as e:
        print(f"⚠️ Lỗi lấy danh mục: {e}")
        return []