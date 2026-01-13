import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, computed_field

from cnm_bookhub_be.db.models.orders import OrderStatus


class OrderItemReq(BaseModel):
    book_id: uuid.UUID
    quantity: int


class OrderReq(BaseModel):
    payment_method: str  # cod, online
    order_items: list[OrderItemReq]


class OrderResp(BaseModel):
    payment_method: str  # cod, online
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


class OrderItemDetailsResp(BaseModel):
    id: uuid.UUID
    book_id: uuid.UUID
    title: str
    author: str
    price: int
    quantity: int
    subtotal: int
    image_urls: str | None


class ShippingInfoResp(BaseModel):
    recipient_name: str | None
    phone_number: str | None
    address: str


class OrderStatusResp(BaseModel):
    id: uuid.UUID
    status: str
    address_at_purchase: str
    payment_method: str
    total_price: int


class OrderDetailsResp(BaseModel):
    id: uuid.UUID
    status: str
    created_at: datetime
    payment_method: str
    order_items: list[OrderItemDetailsResp]
    shipping_info: ShippingInfoResp
    total_price: int

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


class CustomerInfoDTO(BaseModel):
    """Customer information for order list."""

    id: uuid.UUID
    name: str | None
    email: str
    phone: str | None

    model_config = ConfigDict(from_attributes=True)


class OrderItemListDTO(BaseModel):
    """Order item for list view."""

    book_id: uuid.UUID
    title: str
    price: int
    quantity: int
    image_url: str | None
    author: str

    model_config = ConfigDict(from_attributes=True)


class OrderListDTO(BaseModel):
    """Order information for admin list view."""

    id: uuid.UUID
    customer: CustomerInfoDTO
    items: list[OrderItemListDTO]
    total_amount: int
    shipping_fee: int = 0
    status: str
    created_at: datetime
    payment_method: str
    shipping_address: str

    model_config = ConfigDict(from_attributes=True)


class OrderListResponse(BaseModel):
    """Response for order list with pagination."""

    items: list[OrderListDTO]
    total: int
    totalPage: int  # noqa: N815


class AdminOrderItemDetailDTO(BaseModel):
    """Order item for admin detail view."""

    book_id: uuid.UUID
    title: str
    price: int
    quantity: int
    image_url: str | None
    author: str | None

    model_config = ConfigDict(from_attributes=True)


class AdminOrderDetailResp(BaseModel):
    """Order detail response for admin panel."""

    id: uuid.UUID
    created_at: datetime
    payment_method: str  # cod, banking, vnpay
    customer: CustomerInfoDTO
    shipping_address: str
    items: list[AdminOrderItemDetailDTO]
    shipping_fee: int
    total_amount: int
    status: str  # pending, shipping, completed, cancelled

    model_config = ConfigDict(from_attributes=True)