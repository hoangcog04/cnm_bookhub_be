import uuid

from pydantic import BaseModel, ConfigDict


class OrderItemDTO(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    book_id: uuid.UUID
    quantity: int
    price_at_purchase: int

    model_config = ConfigDict(from_attributes=True)


class OrderItemCreateDTO(BaseModel):
    order_id: uuid.UUID
    book_id: uuid.UUID
    quantity: int
    price_at_purchase: int


class OrderItemUpdateDTO(BaseModel):
    quantity: int | None = None
    price_at_purchase: int | None = None
