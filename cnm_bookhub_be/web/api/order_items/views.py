import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from cnm_bookhub_be.db.dao.order_item_dao import OrderItemDAO
from cnm_bookhub_be.db.models.order_items import OrderItem
from cnm_bookhub_be.web.api.order_items.schema import (
    OrderItemDTO,
    OrderItemCreateDTO,
    OrderItemUpdateDTO,
)

router = APIRouter()

@router.get("/", response_model=list[OrderItemDTO])
async def get_order_items(
    limit: int = 10,
    offset: int = 0,
    order_item_dao: OrderItemDAO = Depends(),
) -> list[OrderItem]:
    return await order_item_dao.get_all_order_items(limit, offset)

@router.get("/{order_item_id}", response_model=OrderItemDTO)
async def get_order_item(
    order_item_id: uuid.UUID,
    order_item_dao: OrderItemDAO = Depends(),
) -> OrderItem:
    order_item = await order_item_dao.get_order_item_by_id(order_item_id)
    if order_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found",
        )
    return order_item

@router.get("/by-order/{order_id}", response_model=list[OrderItemDTO])
async def get_items_by_order(
    order_id: uuid.UUID,
    order_item_dao: OrderItemDAO = Depends(),
) -> list[OrderItem]:
    return await order_item_dao.get_order_items_by_order_id(order_id)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=OrderItemDTO)
async def create_order_item(
    new_item: OrderItemCreateDTO,
    order_item_dao: OrderItemDAO = Depends(),
) -> None:
    await order_item_dao.create_order_item(
        order_id=new_item.order_id,
        book_id=new_item.book_id,
        quantity=new_item.quantity,
        price_at_purchase=new_item.price_at_purchase,
    )

@router.put("/{order_item_id}", response_model=OrderItemDTO)
async def update_order_item(
    order_item_id: uuid.UUID,
    payload: OrderItemUpdateDTO,
    order_item_dao: OrderItemDAO = Depends(),
):
    order_item = await order_item_dao.update_order_item(
        order_item_id,
        **payload.model_dump(exclude_unset=True),
    )

    if order_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found",
        )

    return order_item

@router.post(
    "/{order_item_id}/soft-delete",
    status_code=status.HTTP_200_OK,
)


@router.delete("/{order_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order_item(
    order_item_id: uuid.UUID,
    order_item_dao: OrderItemDAO = Depends(),
) -> None:
    success = await order_item_dao.delete_order_item(order_item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found",
        )
