from fastapi import APIRouter, HTTPException, status
from fastapi.param_functions import Depends
from cnm_bookhub_be.db.dao.book_dao import BookDAO
from cnm_bookhub_be.db.models.books import Book
from cnm_bookhub_be.web.api.books.schema import BooksByCategoryDTO, BookDTO

router = APIRouter()

# GET BOOKS BY CATEGORY ID
@router.get("/category/{category_id}", response_model=list[BooksByCategoryDTO])
async def get_books_by_category(
    category_id: int,
    dao: BookDAO = Depends(),
) -> list[Book]:
    books = await dao.get_books_category_id(category_id)
    if not books:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No books found in category {category_id}",
        )
    return books