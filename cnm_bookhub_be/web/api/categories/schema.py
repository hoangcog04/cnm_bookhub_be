from pydantic import BaseModel, ConfigDict

class CategoryDTO(BaseModel):
    id: int
    name: str
    description: str | None = None
    number_of_books: int = 0
    
    model_config = ConfigDict(from_attributes=True)
    
class CategoryInputDTO(BaseModel):
    name: str
    description: str | None = None
    
class CategoryUpdateDTO(BaseModel):
    name: str | None = None
    description: str | None = None

class CategoryListResponse(BaseModel):
    items: list[CategoryDTO]
    totalPage: int