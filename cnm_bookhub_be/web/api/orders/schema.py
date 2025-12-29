import uuid
from pydantic import BaseModel, ConfigDict


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
    status: str
    address_at_purchase: str


class OrderUpdateDTO(BaseModel):
    """DTO for updating an order."""

    status: str | None = None
    address_at_purchase: str | None = None
