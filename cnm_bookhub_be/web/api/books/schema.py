import uuid

from pydantic import BaseModel, ConfigDict


class BookDTO(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    price: int
    stock: int
    image_urls: str | None
    description: str | None
    more_info: dict | None
    category_id: int
    category_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class BookCreateDTO(BaseModel):
    title: str
    author: str
    price: int
    stock: int = 0
    image_urls: str | None = None
    description: str | None = None
    more_info: dict | None = None
    category_id: int


class BookUpdateDTO(BaseModel):
    title: str | None = None
    author: str | None = None
    price: int | None = None
    stock: int | None = None
    image_urls: str | None = None
    description: str | None = None
    more_info: dict | None = None
    category_id: int | None = None


class BooksByCategoryDTO(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    price: int
    stock: int
    image_urls: str | None = None
    description: str | None = None
    more_info: dict | None = None


class BookListResponse(BaseModel):
    items: list[BookDTO]
    totalPage: int
