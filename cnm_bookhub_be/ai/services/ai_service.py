import os
import json
import re
import time
import random
from dotenv import load_dotenv
from google import genai # Thư viện mới
from google.genai import types # Để config
from google.api_core import exceptions
from cnm_bookhub_be.ai.models import SearchState

load_dotenv()

# --- 1. SETUP XOAY VÒNG KEY ---
api_keys_str = os.getenv("GEMINI_API_KEYS", "") # Lấy list key ngăn cách bởi dấu phẩy
API_KEYS = api_keys_str.split(",") if api_keys_str else []

# Fallback nếu chỉ có 1 key lẻ
if not API_KEYS:
    single_key = os.getenv("GEMINI_API_KEY")
    if single_key:
        API_KEYS = [single_key]

print(f"🔑 Đã tải {len(API_KEYS)} API Key. Sẵn sàng xoay vòng!")

current_key_index = 0
MODEL_NAME = 'gemini-3-flash-preview'

# Biến global client để dùng chung (sẽ được cập nhật khi đổi key)
client = None

def get_current_client():
    """Hàm lấy client hiện tại hoặc khởi tạo nếu chưa có"""
    global client, current_key_index
    if client is None:
        if not API_KEYS:
            raise ValueError("❌ Không tìm thấy API Key nào trong .env!")
        client = genai.Client(api_key=API_KEYS[current_key_index])
    return client

def switch_next_key():
    """Hàm chuyển sang key tiếp theo"""
    global client, current_key_index
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    print(f"🔄 Đổi sang Key #{current_key_index + 1}...")
    # Khởi tạo lại client với key mới
    client = genai.Client(api_key=API_KEYS[current_key_index])


# --- 2. HÀM GỌI GEMINI THÔNG MINH (CÚ PHÁP MỚI + ASYNC) ---
async def call_gemini_smart(prompt: str, response_json=False):
    global client
    
    # Thử tối đa số lần bằng số lượng key đang có
    for attempt in range(len(API_KEYS)):
        try:
            active_client = get_current_client()
            
            # Cấu hình trả về JSON hoặc Text
            config = types.GenerateContentConfig(
                temperature=0.5,
                response_mime_type="application/json" if response_json else "text/plain"
            )

            # Gọi Async (aio) để không chặn server
            response = await active_client.aio.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=config
            )
            return response.text
            
        except Exception as e:
            # Kiểm tra lỗi Quota (429 Resource Exhausted)
            # Lưu ý: Thư viện mới đôi khi ném lỗi khác nhau, nên check chuỗi lỗi cho chắc
            error_str = str(e).lower()
            if "429" in error_str or "quota" in error_str or "exhausted" in error_str:
                print(f"⚠️ Key #{current_key_index + 1} đã hết hạn mức! Đang đổi Key khác...")
                switch_next_key()
                time.sleep(1) # Nghỉ 1 xíu rồi retry
                continue # Thử lại vòng lặp với key mới
            else:
                print(f"❌ Lỗi Gemini (Không phải do quota): {e}")
                raise e # Lỗi khác thì bắn ra luôn

    raise Exception("❌ Tất cả API Key đều đã hết hạn mức!")


# --- 3. HÀM EXTRACT INTENT ---
async def extract_intent(current_state: SearchState, user_msg: str, valid_categories: list) -> SearchState:    
    categories_str = ", ".join([f'"{c}"' for c in valid_categories])

    prompt = f"""
    Bạn là trợ lý AI thông minh quản lý bộ lọc tìm kiếm sách cho hệ thống BookHub.
    
    1. INPUT:
    - State hiện tại: {current_state.model_dump_json()}
    - User nói: "{user_msg}"
    - DANH SÁCH CHỦ ĐỀ CÓ TRONG KHO (DB): [{categories_str}]

    2. NHIỆM VỤ: Phân tích và Update state JSON.
    
    A. XỬ LÝ TÊN SÁCH:
       - Nếu user nhắc tên sách cụ thể -> Update "book_name".
       - Nếu đổi sách -> Update "book_name" mới.

    B. XỬ LÝ SỐ LƯỢNG:
       - Có số cụ thể -> Update quantity.
       - KHÔNG nhắc số -> Reset quantity = 3.

    C. XỬ LÝ NGỮ CẢNH (CONTEXT):
       - User hỏi TÊN SÁCH mới hoặc THỂ LOẠI mới -> Reset các trường cũ.
       - User chỉ hỏi GIÁ/TÍNH CHẤT (rẻ, hay...) -> Giữ nguyên context.

    D. XỬ LÝ GIÁ:
       - "giá sinh viên", "rẻ" -> max_price = 100000.
       - Số cụ thể (dưới 200k) -> max_price = 200000.
       
    E. CHUẨN HÓA TÊN: Sửa lỗi chính tả tên sách/tác giả.

    F. XỬ LÝ CATEGORY:
       - Chỉ điền 'category' nếu khớp (hoặc đồng nghĩa) với danh sách [{categories_str}].
       - Map từ đồng nghĩa về tên chuẩn.
       - Không khớp -> null.

    3. OUTPUT JSON MẪU:
    {{ "query": "...", "book_name": "Nhà Giả Kim", "author": null, "category": "Lãng mạn", "min_price": null, "max_price": null, "quantity": 3 }}
    """

    try:
        # Gọi hàm smart với chế độ JSON=True
        text_response = await call_gemini_smart(prompt, response_json=True)
        
        # Clean data (phòng hờ)
        text_response = text_response.strip()
        if text_response.startswith("```"):
            text_response = re.sub(r"^```json|^```|```$", "", text_response).strip()
            
        data = json.loads(text_response)
        return SearchState(**data)
        
    except Exception as e:
        print(f"⚠️ Lỗi AI Extract Intent: {e}")
        # Trả về state cũ thay vì crash
        return current_state


# --- 4. HÀM GENERATE RESPONSE ---
async def generate_chat_response(user_msg: str, found_books: list, has_greeted: bool) -> str:
    
    if not found_books:
        return "Tiếc quá, mình tìm theo yêu cầu của bạn thì chưa thấy cuốn nào phù hợp trong kho. Bạn thử nới rộng khoảng giá hoặc tìm chủ đề khác xem sao nhé?"

    context_text = ""
    for i, book in enumerate(found_books, 1):
        price_str = "{:,}".format(book['price'])
        context_text += f"{i}. {book['title']} - Giá: {price_str}đ - Tác giả: {book['author']}\n"

    if not has_greeted:
        tone_instruction = "- Đây là lần đầu gặp khách: Hãy BẮT ĐẦU bằng lời chào thân thiện (VD: Chào bạn, BookHub xin chào...)."
    else:
        tone_instruction = "- Đây là đoạn chat tiếp theo: TUYỆT ĐỐI KHÔNG chào lại (Không nói 'Chào bạn' nữa). Hãy đi thẳng vào câu trả lời hoặc nhận xét về sách."
        
    prompt = f"""
    Bạn là nhân viên bán sách thông minh, thân thiện.
    
    THÔNG TIN ĐẦU VÀO:
    1. KHÁCH HỎI: "{user_msg}"
    2. KẾT QUẢ TÌM KIẾM ({len(found_books)} cuốn):
    {context_text}
    
    NHIỆM VỤ:
    - Nếu sách KHỚP: Giới thiệu nhiệt tình.
    - Nếu sách GẦN GIỐNG (Sai chính tả): Mạnh dạn gợi ý "Có phải ý bạn là...".
    - Nếu sách KHÁC (Gợi ý thay thế): Nói "Hiện chưa có cuốn đó, nhưng mình có cuốn này hay lắm...".

    YÊU CẦU:
    - Giọng văn thân thiện, ngắn gọn.
    - KHÔNG hiển thị JSON, chỉ trả về lời thoại.
    """
    
    try:
        # Gọi hàm smart với chế độ JSON=False (Text)
        return await call_gemini_smart(prompt, response_json=False)
    except Exception as e:
        print(f"Lỗi generate response: {e}")
        return "Hệ thống đang bận, nhưng bạn xem danh sách sách bên dưới nhé!"