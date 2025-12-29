import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from cnm_bookhub_be.db.dao.order_dao import OrderDAO
from cnm_bookhub_be.db.models.orders import Order
from cnm_bookhub_be.web.api.orders.schema import (
    OrderDTO,
    OrderCreateDTO,
    OrderUpdateDTO,
)

router = APIRouter()


@router.get("/", response_model=list[OrderDTO])
async def get_orders(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_dao: OrderDAO = Depends(),
) -> list[Order]:
    """Get all orders."""
    return await order_dao.get_all_orders(limit=limit, offset=offset)


@router.get("/{order_id}", response_model=OrderDTO)
async def get_order(
    order_id: uuid.UUID,
    order_dao: OrderDAO = Depends(),
) -> Order:
    """Get order by ID."""
    order = await order_dao.get_order_by_id(order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return order


@router.post("/", response_model=OrderDTO, status_code=status.HTTP_201_CREATED)
async def create_order(
    new_order: OrderCreateDTO,
    order_dao: OrderDAO = Depends(),
) -> Order:
    """Create new order."""
    return await order_dao.create_order(
        user_id=new_order.user_id,
        status=new_order.status,
        address_at_purchase=new_order.address_at_purchase,
    )


@router.patch("/{order_id}", response_model=OrderDTO)
async def update_order(
    order_id: uuid.UUID,
    order_update: OrderUpdateDTO,
    order_dao: OrderDAO = Depends(),
) -> Order:
    """Update order."""
    order = await order_dao.update_order(
        order_id=order_id,
        status=order_update.status,
        address_at_purchase=order_update.address_at_purchase,
    )
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: uuid.UUID,
    order_dao: OrderDAO = Depends(),
) -> None:
    """Delete order."""
    success = await order_dao.delete_order(order_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
@router.post("/{order_id}/soft-delete", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_order(
    order_id: uuid.UUID,
    order_dao: OrderDAO = Depends(),
) -> None:
    success = await order_dao.soft_delete_order(order_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )