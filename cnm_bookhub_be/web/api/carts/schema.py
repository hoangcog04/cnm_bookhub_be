from pydantic import BaseModel
from uuid import UUID


class CartItemDTO(BaseModel):
    book_id: UUID
    quantity: int

    class Config:
        from_attributes = True


class AddCartItemDTO(BaseModel):
    book_id: UUID
    quantity: int


class UpdateCartItemDTO(BaseModel):
    quantity: int
