import uuid
from datetime import datetime, timezone

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from cnm_bookhub_be.db.dependencies import get_db_session
from cnm_bookhub_be.db.models.books import Book
from cnm_bookhub_be.db.models.order_items import OrderItem
from cnm_bookhub_be.db.models.orders import Order, OrderStatus
from cnm_bookhub_be.db.models.provinces import Province
from cnm_bookhub_be.db.models.users import User
from cnm_bookhub_be.db.models.wards import Ward
from cnm_bookhub_be.web.api.orders.schema import (
    BookInfoHistoryResp,
    OrderDetailsResp,
    OrderHistoryResp,
    OrderItemDetailsResp,
    OrderItemHistoryResp,
    OrderReq,
    OrderStatusResp,
    ShippingInfoResp,
)


class OrderDAO:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    async def create_order(
        self,
        user_id: uuid.UUID,
        status: str,
        address_at_purchase: str,
    ) -> Order:
        order = Order(
            user_id=user_id,
            status=status,
            address_at_purchase=address_at_purchase,
        )
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def get_all_orders(
        self,
        limit: int,
        offset: int,
    ) -> list[Order]:
        result = await self.session.execute(
            select(Order).limit(limit).offset(offset),
        )
        return list(result.scalars().fetchall())

    async def get_order_by_id(
        self,
        order_id: uuid.UUID,
    ) -> Order | None:
        result = await self.session.execute(
            select(Order).where(Order.id == order_id),
        )
        return result.scalar_one_or_none()

    async def update_order(
        self,
        order_id: uuid.UUID,
        status: str | None = None,
        address_at_purchase: str | None = None,
    ) -> Order | None:
        order = await self.get_order_by_id(order_id)
        if order is None:
            return None

        if status is not None:
            order.status = status
        if address_at_purchase is not None:
            order.address_at_purchase = address_at_purchase

        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def soft_delete_order(self, order_id: uuid.UUID) -> bool:
        result = await self.session.execute(
            select(Order).where(Order.id == order_id),
        )
        order = result.scalar_one_or_none()

        if order is None:
            return False

        order.deleted = True
        order.deleted_at = datetime.now(timezone.utc)

        await self.session.commit()
        return True

    async def get_history_order(self, user_id: uuid.UUID) -> list[Order] | None:
        results = await self.session.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.order_items).selectinload(OrderItem.book))
            .order_by(Order.created_at.desc())
        )
        return list(results.unique().scalars().fetchall())

    async def get_orders_by_user_and_status(
        self,
        user_id: uuid.UUID,
        status: str,
    ) -> list[Order]:
        results = await self.session.execute(
            select(Order)
            .where(Order.user_id == user_id, Order.status == status)
            .options(selectinload(Order.order_items).selectinload(OrderItem.book))
            .order_by(Order.created_at.desc())
        )
        return list(results.unique().scalars().fetchall())

    async def create_pending_order(
        self,
        user: User,
        order_request: OrderReq,
        payment_method: str,
    ) -> tuple[Order, int]:
        req_order_items = order_request.order_items

        if payment_method == "online":
            order_status = OrderStatus.REQUIRE_PAYMENT
        else:
            order_status = OrderStatus.WAITING_FOR_CONFIRMATION

        req_book_ids = [req_order_item.book_id for req_order_item in req_order_items]
        results = await self.session.execute(
            select(Book).where(Book.id.in_(req_book_ids)),
        )
        books = list(results.scalars().all())

        req_order_item_quantities = {
            req_order_item.book_id: req_order_item.quantity
            for req_order_item in req_order_items
        }
        total_price = 0
        for book in books:
            quantity = req_order_item_quantities[book.id]
            total_price += book.price * quantity

        result = await self.session.execute(
            select(Ward)
            .where(Ward.code == user.ward_code)
            .options(selectinload(Ward.province)),
        )
        ward = result.scalar_one_or_none()
        if ward is None:
            raise HTTPException(status_code=400, detail="Địa chỉ không hợp lệ")

        address_at_purchase = (
            f"{user.address_detail}, {ward.full_name}, {ward.province.full_name}"
        )
        order = Order(
            user_id=user.id,
            status=order_status,
            address_at_purchase=address_at_purchase,
            total_price=total_price,
        )

        self.session.add(order)
        await self.session.flush()

        order_id = order.id
        order_items = [
            OrderItem(
                order_id=order_id,
                book_id=book.id,
                quantity=req_order_item_quantities[book.id],
                price_at_purchase=book.price,
            )
            for book in books
        ]
        self.session.add_all(order_items)

        await self.session.commit()

        return order, total_price

    async def update_payment_intent_id(
        self, order_id: uuid.UUID, payment_intent_id: str
    ) -> bool:
        result = await self.session.execute(
            select(Order).where(Order.id == order_id),
        )
        order = result.scalar_one_or_none()

        if order is None:
            return False

        order.payment_intent_id = payment_intent_id

        await self.session.commit()

        return True

    async def mask_order_as_charged(self, payment_intent_id: str) -> bool:
        result = await self.session.execute(
            select(Order).where(Order.payment_intent_id == payment_intent_id),
        )
        order = result.scalar_one_or_none()

        if order is None:
            return False

        order.status = OrderStatus.WAITING_FOR_CONFIRMATION

        await self.session.commit()

        return True

    async def mask_order_status(self, order_id: uuid.UUID, status: OrderStatus) -> bool:
        if status not in [
            OrderStatus.WAITING_FOR_CONFIRMATION,
            OrderStatus.DELIVERY_IN_PROGRESS,
        ]:
            raise HTTPException(status_code=400, detail="Invalid status")

        result = await self.session.execute(
            select(Order).where(Order.id == order_id),
        )
        order = result.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")

        order_status = order.status
        if order_status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
            raise HTTPException(
                status_code=400, detail="Order is already completed or cancelled"
            )

        order.status = status

        await self.session.commit()

        return True

    async def get_order_history(self, user_id: uuid.UUID) -> list[OrderHistoryResp]:
        results = await self.session.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.order_items).selectinload(OrderItem.book))
            .order_by(Order.created_at.desc())
        )
        orders = list(results.unique().scalars().fetchall())

        order_history_list = []
        for order in orders:
            order_items_resp = []
            for order_item in order.order_items:
                book_info = BookInfoHistoryResp(
                    id=order_item.book.id,
                    title=order_item.book.title,
                    author=order_item.book.author,
                    price=order_item.book.price,
                    created_at=order_item.book.created_at,
                    description=order_item.book.description,
                    image_urls=order_item.book.image_urls,
                )
                order_item_resp = OrderItemHistoryResp(
                    id=order_item.id,
                    quantity=order_item.quantity,
                    price_at_purchase=order_item.price_at_purchase,
                    created_at=order_item.created_at,
                    book=book_info,
                )
                order_items_resp.append(order_item_resp)

            status_str = str(order.status)
            order_history = OrderHistoryResp(
                id=order.id,
                status=status_str,
                address_at_purchase=order.address_at_purchase,
                created_at=order.created_at,
                total_price=order.total_price,
                order_items=order_items_resp,
            )
            order_history_list.append(order_history)

        return order_history_list

    async def get_order_details(self, order_id: uuid.UUID) -> OrderDetailsResp | None:
        result = await self.session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.order_items).selectinload(OrderItem.book),
                selectinload(Order.user),
            )
        )
        order = result.unique().scalar_one_or_none()

        if order is None:
            return None

        payment_method = "online" if order.payment_intent_id else "cod"

        order_items_details = []
        for order_item in order.order_items:
            subtotal = order_item.quantity * order_item.price_at_purchase
            order_item_detail = OrderItemDetailsResp(
                id=order_item.id,
                book_id=order_item.book_id,
                title=order_item.book.title,
                author=order_item.book.author,
                price=order_item.price_at_purchase,
                quantity=order_item.quantity,
                subtotal=subtotal,
                image_urls=order_item.book.image_urls,
            )
            order_items_details.append(order_item_detail)

        shipping_info = ShippingInfoResp(
            recipient_name=order.user.full_name,
            phone_number=order.user.phone_number,
            address=order.address_at_purchase,
        )

        return OrderDetailsResp(
            id=order.id,
            status=str(order.status),
            created_at=order.created_at,
            payment_method=payment_method,
            order_items=order_items_details,
            shipping_info=shipping_info,
            total_price=order.total_price,
        )

    async def get_order_status(self, order_id: uuid.UUID) -> OrderStatusResp | None:
        result = await self.session.execute(
            select(Order).where(Order.id == order_id),
        )
        order = result.scalar_one_or_none()
        if order is None:
            return None
        return OrderStatusResp(
            id=order.id,
            status=str(order.status),
            address_at_purchase=order.address_at_purchase,
            payment_method="online" if order.payment_intent_id else "cod",
            total_price=order.total_price,
        )
