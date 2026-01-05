import uuid
from pydantic import BaseModel, ConfigDict

class BookDTO(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    price: float
    stock: int
    image_urls: str | None = None
    description: str | None = None
    more_info: dict | None = None
    category_id: int
    
    model_config = ConfigDict(from_attributes=True)
    
class BooksByCategoryDTO(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    price: float
    stock: int
    image_urls: str | None = None
    description: str | None = None
    
    model_config = ConfigDict(from_attributes=True)