from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from cnm_bookhub_be.db.dao.cart_dao import CartDAO
from cnm_bookhub_be.web.api.carts.schema import (
    AddCartItemDTO,
    CartItemDTO,
    UpdateCartItemDTO,
)

router = APIRouter()


@router.get("/", response_model=list[CartItemDTO])
async def get_cart(
    user_id: UUID,
    cart_dao: CartDAO = Depends(),
):
    return await cart_dao.get_user_cart(user_id)


@router.post("/items")
async def add_item(
    user_id: UUID,
    payload: AddCartItemDTO,
    cart_dao: CartDAO = Depends(),
):
    return await cart_dao.add_or_increment(
        user_id,
        payload.book_id,
        payload.quantity,
    )


@router.put("/items/{book_id}")
async def update_item(
    user_id: UUID,
    book_id: UUID,
    payload: UpdateCartItemDTO,
    cart_dao: CartDAO = Depends(),
):
    item = await cart_dao.update_quantity(
        user_id,
        book_id,
        payload.quantity,
    )
    if not item:
        raise HTTPException(404, "Item not found")
    return item


@router.post("/items/{book_id}")
async def remove_item(
    user_id: UUID,
    book_id: UUID,
    cart_dao: CartDAO = Depends(),
):
    if not await cart_dao.soft_delete(user_id, book_id):
        raise HTTPException(404, "Item not found")


@router.delete(
    "/items/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def hard_delete_cart_item(
    user_id: UUID,
    book_id: UUID,
    cart_dao: CartDAO = Depends(),
):
    deleted = await cart_dao.hard_delete(user_id, book_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found",
        )
