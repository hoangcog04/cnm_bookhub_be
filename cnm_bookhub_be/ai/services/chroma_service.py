import chromadb
from chromadb.utils import embedding_functions
from cnm_bookhub_be.ai.models import SearchState
import os
import difflib  # <--- THÊM THƯ VIỆN NÀY (Có sẵn trong Python)

vietnamese_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

chroma_client = chromadb.PersistentClient(path="./chroma_db") 

collection = chroma_client.get_or_create_collection(
    name="books_store",
    embedding_function=vietnamese_ef
)

# Biến toàn cục lưu danh sách tác giả để so khớp
ALL_AUTHORS = set()

def add_books_to_chroma(books_data: list):
    global ALL_AUTHORS
    
    # Cập nhật danh sách tác giả
    for book in books_data:
        if book.get("author"):
            ALL_AUTHORS.add(book["author"])

    # Kiểm tra xem trong kho đã có sách chưa
    existing_count = collection.count()
    if existing_count > 0:
        print(f"⚡ Dữ liệu đã có sẵn ({existing_count} cuốn).")
        return

    print("⏳ Đang tính toán Vector cho sách lần đầu...")
    
    ids = []
    documents = []
    metadatas = []

    for book in books_data:
        ids.append(str(book["id"]))
        
        # Thêm tên sách vào nội dung embed
        content_to_embed = f"{book['title']}. Tác giả: {book['author']}. Thể loại: {book['category']}. Nội dung: {book['description']}"
        documents.append(content_to_embed)
        
        metadatas.append({
            "price": book["price"],
            "author": book["author"],
            "category": book["category"],
            "title": book["title"]  # <--- [QUAN TRỌNG] THÊM TITLE VÀO METADATA
        })

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    print(f"✅ Đã nạp xong {len(ids)} cuốn sách.")

def search_books_chroma(state: SearchState):
    global ALL_AUTHORS
    print(f"🔍 Input ban đầu: {state}")

    # --- BƯỚC 1: AUTO-CORRECT TÊN TÁC GIẢ ---
    search_author = state.author
    if search_author and ALL_AUTHORS:
        matches = difflib.get_close_matches(search_author, list(ALL_AUTHORS), n=1, cutoff=0.6)
        if matches:
            suggested_author = matches[0]
            if suggested_author.lower() != search_author.lower():
                print(f"✨ Auto-Correct: Đã sửa '{search_author}' -> '{suggested_author}'")
                search_author = suggested_author

    # --- BƯỚC 2: TẠO QUERY VECTOR ---
    final_query = state.query if state.query else ""
    
    # Cộng dồn tất cả thông tin vào câu truy vấn ngữ nghĩa
    if state.book_name:
        final_query += f" sách có tên {state.book_name}"
    if search_author:
        final_query += f" sách của tác giả {search_author}"
    if state.category:
        final_query += f" thuộc thể loại {state.category}"
        
    if not final_query.strip():
        final_query = "sách hay nên đọc"

    print(f"   -> Query vector (Sau fix): '{final_query}'")

    # --- BƯỚC 3: VECTOR SEARCH (LẤY 50 CUỐN) ---
    results = collection.query(
        query_texts=[final_query],
        n_results=50, 
        where=build_price_filter(state)
    )
    
    if not results['ids'] or not results['ids'][0]:
        return []

    raw_ids = results['ids'][0]
    raw_metadatas = results['metadatas'][0]

    # --- BƯỚC 4: LỌC ỨNG VIÊN (CANDIDATES) ---
    candidates = [] 
    
    # Kiểm tra xem có cần lọc Strict không (Có Tác giả OR Thể loại OR Tên sách)
    has_strict_filter = bool(search_author or state.category or state.book_name)

    for i, meta in enumerate(raw_metadatas):
        is_match = True
        
        if has_strict_filter:
            # A. Check Tên Sách (Quan trọng: Dùng 'in' để tìm tương đối)
            if state.book_name:
                db_title = meta.get("title", "").lower() # Cần đảm bảo metadata có title
                search_title = state.book_name.lower()
                if search_title not in db_title:
                    is_match = False

            # B. Check Tác giả
            if search_author and is_match:
                db_author = meta.get("author", "").lower()
                if search_author.lower() not in db_author:
                    is_match = False
            
            # C. Check Thể loại
            if state.category and is_match:
                db_cat = meta.get("category", "").lower()
                if state.category.lower() not in db_cat:
                    is_match = False
        
        # Nếu thỏa mãn mọi điều kiện thì đưa vào danh sách ứng viên
        if is_match:
            candidates.append({
                "id": raw_ids[i],
                "price": meta.get("price", 0),
                "data": meta
            })

    # --- BƯỚC 5: XỬ LÝ KẾT QUẢ & SẮP XẾP ---
    final_results = []
    
    # TH1: Có ứng viên khớp bộ lọc Strict -> Dùng danh sách này
    if candidates:
        print(f"   ✅ Tìm thấy {len(candidates)} ứng viên khớp tiêu chí.")
        final_results = candidates
    else:
        # TH2: Fallback - Nếu lọc Strict rỗng -> Dùng kết quả Vector gốc
        print(f"   ⚠️ Không tìm thấy khớp chính xác. Dùng kết quả Vector gốc.")
        for i, _id in enumerate(raw_ids):
            final_results.append({
                "id": _id,
                "price": raw_metadatas[i].get("price", 0)
            })

    # --- SẮP XẾP (SORTING) ---
    # Nếu user đặt max_price (quan tâm giá rẻ) -> Sắp xếp giá thấp đến cao
    if state.max_price is not None:
        print("   💰 User quan tâm giá -> Sắp xếp: Giá thấp đến cao.")
        final_results.sort(key=lambda x: x["price"])
    else:
        # Nếu không, giữ nguyên thứ tự Vector (Độ liên quan ngữ nghĩa)
        print("   🧠 User quan tâm nội dung -> Giữ nguyên thứ tự Vector.")

    # --- BƯỚC 6: CẮT ĐÚNG SỐ LƯỢNG ---
    final_ids = [item["id"] for item in final_results[:state.quantity]]
    
    return final_ids

# Hàm phụ để tạo bộ lọc giá cho gọn
def build_price_filter(state):
    conditions = []
    if state.min_price is not None:
        conditions.append({"price": {"$gte": state.min_price}})
    if state.max_price is not None:
        conditions.append({"price": {"$lte": state.max_price}})
    
    if len(conditions) > 1: return {"$and": conditions}
    elif len(conditions) == 1: return conditions[0]
    return None