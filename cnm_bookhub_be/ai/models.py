from pydantic import BaseModel
from typing import Optional

class Book(BaseModel):
    id: str
    title: str
    author: str
    price: int
    category: str
    description: str
    image_url: str

class SearchState(BaseModel):
    query: Optional[str] = None
    book_name: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    quantity: int = 3
    has_greeted: bool = False

class ChatRequest(BaseModel):
    user_id: str
    message: str