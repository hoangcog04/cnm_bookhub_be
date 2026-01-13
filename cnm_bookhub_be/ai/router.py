import asyncio

from fastapi import APIRouter
from typing import Dict
from .models import ChatRequest, SearchState
from .services.chroma_service import search_books_chroma
from .services.db_service import get_unique_categories
from .services.ai_service import extract_intent, generate_chat_response

USER_SESSIONS: Dict[str, SearchState] = {}
BOOKS_CACHE: Dict[str, dict] = {}
VALID_CATEGORIES_CACHE = []

router = APIRouter(prefix="/chat", tags=["AI Chat Assistant"])

@router.post("")
async def chat_endpoint(request: ChatRequest):
    user_id = request.user_id
    user_msg = request.message
    
    if user_id not in USER_SESSIONS:
        USER_SESSIONS[user_id] = SearchState()
    current_state = USER_SESSIONS[user_id]

    categories_to_use = VALID_CATEGORIES_CACHE if VALID_CATEGORIES_CACHE else get_unique_categories()
    new_state = await extract_intent(current_state, user_msg, categories_to_use)
    new_state.has_greeted = current_state.has_greeted
    USER_SESSIONS[user_id] = new_state
    
    found_ids = await asyncio.to_thread(search_books_chroma, new_state) 

    found_books_detail = []
    for book_id in found_ids:
        if str(book_id) in BOOKS_CACHE:
            found_books_detail.append(BOOKS_CACHE[str(book_id)])
    
    bot_response = await generate_chat_response(user_msg, found_books_detail, new_state.has_greeted)
    
    new_state.has_greeted = True
    USER_SESSIONS[user_id] = new_state

    return {
        "response": bot_response,
        "data": found_books_detail,
        "state": new_state
    }