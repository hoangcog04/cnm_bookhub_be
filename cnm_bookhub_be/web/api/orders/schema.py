import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, computed_field

from cnm_bookhub_be.db.models.orders import OrderStatus


class OrderItemReq(BaseModel):
    book_id: uuid.UUID
    quantity: int


class OrderReq(BaseModel):
    address_at_purchase: str
    order_items: list[OrderItemReq]


class OrderResp(BaseModel):
    id: uuid.UUID
    payment_intent_id: str


class BookInfoHistoryResp(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    price: int
    created_at: datetime
    description: str | None
    image_urls: str | None


class OrderItemHistoryResp(BaseModel):
    id: uuid.UUID
    quantity: int
    price_at_purchase: int
    created_at: datetime
    book: BookInfoHistoryResp


class OrderHistoryResp(BaseModel):
    id: uuid.UUID
    status: str
    address_at_purchase: str
    created_at: datetime
    total_price: int
    order_items: list[OrderItemHistoryResp]


class OrderDTO(BaseModel):
    """DTO for returning order data."""

    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    address_at_purchase: str

    model_config = ConfigDict(from_attributes=True)


class OrderCreateDTO(BaseModel):
    """DTO for creating an order."""

    user_id: uuid.UUID
    status: OrderStatus
    address_at_purchase: str


class OrderUpdateDTO(BaseModel):
    """DTO for updating an order."""

    status: str | None = None
    address_at_purchase: str | None = None


class BookInfoDTO(BaseModel):
    """Basic book information for order items."""

    id: uuid.UUID
    title: str
    model_config = ConfigDict(from_attributes=True)


class OrderItemWithBookDTO(BaseModel):
    """Order item with book details."""

    id: uuid.UUID
    book_id: uuid.UUID
    quantity: int
    price_at_purchase: int
    book: BookInfoDTO
    model_config = ConfigDict(from_attributes=True)


class OrderHistoryDTO(BaseModel):
    """Order with items and book details for history."""

    id: uuid.UUID
    status: str
    address_at_purchase: str
    created_at: datetime
    order_items: list[OrderItemWithBookDTO]

    @computed_field
    @property
    def total_amount(self) -> int:
        """Calculate total amount from order items."""
        return sum(item.quantity * item.price_at_purchase for item in self.order_items)

    @computed_field
    @property
    def total_items(self) -> int:
        """Calculate total number of items."""
        return len(self.order_items)

    model_config = ConfigDict(from_attributes=True)
