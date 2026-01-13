import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from cnm_bookhub_be.db.dao.cart_dao import CartDAO
from cnm_bookhub_be.db.dao.order_dao import OrderDAO
from cnm_bookhub_be.db.models.orders import Order, OrderStatus
from cnm_bookhub_be.db.models.users import User, current_active_user
from cnm_bookhub_be.services.stripe_service import stripe_service
from cnm_bookhub_be.web.api.orders.schema import (
    AdminOrderDetailResp,
    CustomerInfoDTO,
    OrderCreateDTO,
    OrderDetailsResp,
    OrderDTO,
    OrderHistoryResp,
    OrderItemListDTO,
    OrderListDTO,
    OrderListResponse,
    OrderReq,
    OrderResp,
    OrderStatusResp,
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


@router.get("/getAll", response_model=OrderListResponse)
async def get_all_orders(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(1, ge=1),
    order_id: str | None = Query(None),
    order_status: str | None = Query(None),
    order_date: str | None = Query(None),
    order_dao: OrderDAO = Depends(),
) -> OrderListResponse:
    """Get all orders with filters and pagination for admin."""
    # Convert offset from 1-based to 0-based
    offset_0_based = (offset - 1) * limit

    orders, total = await order_dao.get_all_orders_with_filters(
        limit=limit,
        offset=offset_0_based,
        order_id=order_id,
        order_status=order_status,
        order_date=order_date,
    )

    # Transform orders to OrderListDTO
    order_list_items = []
    for order in orders:
        # Map status to frontend format
        frontend_status = order_dao.map_status_to_frontend(order.status)

        # Build customer info
        customer = CustomerInfoDTO(
            id=order.user.id,
            name=order.user.full_name,
            email=order.user.email,
            phone=order.user.phone_number,
        )

        # Build order items
        items = []
        for order_item in order.order_items:
            item = OrderItemListDTO(
                book_id=order_item.book_id,
                title=order_item.book.title,
                price=order_item.price_at_purchase,
                quantity=order_item.quantity,
                image_url=order_item.book.image_urls.split(",")[0]
                if order_item.book.image_urls
                else None,
                author=order_item.book.author,
            )
            items.append(item)

        # Calculate shipping fee (assuming 30000 VND, can be adjusted)
        shipping_fee = 30000 if order.total_price < 500000 else 0

        order_dto = OrderListDTO(
            id=order.id,
            customer=customer,
            items=items,
            total_amount=order.total_price,
            shipping_fee=shipping_fee,
            status=frontend_status,
            created_at=order.created_at,
            payment_method="online" if order.payment_intent_id else "cod",
            shipping_address=order.address_at_purchase,
        )
        order_list_items.append(order_dto)

    total_pages = (total + limit - 1) // limit if total > 0 else 1

    return OrderListResponse(
        items=order_list_items,
        total=total,
        totalPage=total_pages,
    )


@router.get("/history", response_model=list[OrderHistoryResp])
async def get_order_history(
    user: User = Depends(current_active_user),
    order_dao: OrderDAO = Depends(),
) -> list[OrderHistoryResp]:
    return await order_dao.get_order_history(user.id)


# @router.get("/{order_id}", response_model=OrderDTO)
# async def get_order(
#     order_id: uuid.UUID,
#     order_dao: OrderDAO = Depends(),
# ) -> Order:
#     """Get order by ID."""
#     order = await order_dao.get_order_by_id(order_id)
#     if order is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Order not found",
#         )
#     return order


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


@router.post(
    "/request-order", status_code=status.HTTP_201_CREATED, response_model=OrderResp
)
async def request_order(
    order_request: OrderReq,
    user: User = Depends(current_active_user),
    order_dao: OrderDAO = Depends(),
    cart_dao: CartDAO = Depends(),
) -> OrderResp:
    payment_method = order_request.payment_method.lower()

    order, total_price_for_payment = await order_dao.create_pending_order(
        user, order_request, payment_method
    )

    payment_intent_id = ""
    if payment_method == "online":
        payment_intent = await stripe_service.create_payment_intent(
            amount=total_price_for_payment,
            currency="vnd",
        )
        await order_dao.update_payment_intent_id(order.id, payment_intent.id)
        payment_intent_id = payment_intent.client_secret or ""

    await cart_dao.clear_cart(user.id)

    return OrderResp(
        payment_method=payment_method,
        id=order.id,
        payment_intent_id=payment_intent_id,
    )


@router.get(
    "/admin/{order_id}",
    status_code=status.HTTP_200_OK,
    response_model=AdminOrderDetailResp,
)
async def get_admin_order_details(
    order_id: uuid.UUID,
    order_dao: OrderDAO = Depends(),
) -> AdminOrderDetailResp:
    """Get order details for admin panel."""
    order_data = await order_dao.get_admin_order_details(order_id)
    if order_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return AdminOrderDetailResp(**order_data)


@router.patch(
    "/admin/{order_id}/status",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def update_admin_order_status(
    order_id: uuid.UUID,
    order_update: OrderUpdateDTO,
    order_dao: OrderDAO = Depends(),
) -> None:
    """Update order status for admin panel."""
    if not order_update.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status is required",
        )

    # Validate status
    try:
        order_status = OrderStatus(order_update.status)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {order_update.status}",
        ) from err

    # Use mask_order_status for all valid statuses
    await order_dao.mask_order_status(order_id, order_status)


@router.get(
    "/{order_id}", status_code=status.HTTP_200_OK, response_model=OrderDetailsResp
)
async def get_order_details(
    order_id: uuid.UUID,
    order_dao: OrderDAO = Depends(),
) -> OrderDetailsResp:
    order_details = await order_dao.get_order_details(order_id)
    if order_details is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return order_details


@router.get(
    "/{order_id}/status",
    status_code=status.HTTP_200_OK,
    response_model=OrderStatusResp,
)
async def get_order_status(
    order_id: uuid.UUID,
    order_dao: OrderDAO = Depends(),
) -> OrderStatusResp:
    order_status = await order_dao.get_order_status(order_id)
    if order_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return order_status
