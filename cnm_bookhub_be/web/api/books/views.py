import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from cnm_bookhub_be.db.dao.book_dao import BookDAO
from cnm_bookhub_be.db.models.books import Book
from cnm_bookhub_be.web.api.books.schema import (BookDTO,BookCreateDTO,BookUpdateDTO, BooksByCategoryDTO)

router = APIRouter()

@router.get("/", response_model=list[BookDTO])
async def get_books(
    limit: int = 10,
    offset: int = 0,
    book_dao: BookDAO = Depends(),
) -> list[Book]:
    return await book_dao.get_books(limit=limit, offset=offset)

@router.get("/{book_id}", response_model=BookDTO)
async def get_book_by_id(
    book_id: uuid.UUID,
    book_dao: BookDAO = Depends(),
) -> Book:
    book = await book_dao.get_book_by_id(book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    return book

@router.post("/", response_model=BookDTO, status_code=status.HTTP_201_CREATED)
async def create_book(
    payload: BookCreateDTO,
    book_dao: BookDAO = Depends(),
) -> Book:
    return await book_dao.create_book(
        title=payload.title,
        author=payload.author,
        price=payload.price,
        stock=payload.stock,
        image_urls=payload.image_urls,
        description=payload.description,
        more_info=payload.more_info,
        category_id=payload.category_id,
    )

@router.put("/{book_id}", response_model=BookDTO)
async def update_book(
    book_id: uuid.UUID,
    payload: BookUpdateDTO,
    book_dao: BookDAO = Depends(),
) -> Book:
    book = await book_dao.update_book(
        book_id,
        **payload.model_dump(exclude_unset=True),
    )
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    return book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: uuid.UUID,
    book_dao: BookDAO = Depends(),
) -> None:
    success = await book_dao.delete_book(book_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

@router.post("/{book_id}/soft-delete")
async def soft_delete_book(
    book_id: uuid.UUID,
    book_dao: BookDAO = Depends(),
) -> None:
    success = await book_dao.soft_delete_book(book_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found or already deleted",
        )
        
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
