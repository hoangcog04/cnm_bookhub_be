from uuid import UUID

from pydantic import BaseModel


class CartItemDTO(BaseModel):
    book_id: UUID
    quantity: int
    title: str
    author: str
    price: int
    image_urls: str | None = None

    class Config:
        from_attributes = True


class AddCartItemDTO(BaseModel):
    book_id: UUID
    quantity: int


class UpdateCartItemDTO(BaseModel):
    quantity: int
