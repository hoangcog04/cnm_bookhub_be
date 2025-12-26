from pydantic import BaseModel, ConfigDict

class CategoryDTO(BaseModel):
    id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)
    
class CategoryInputDTO(BaseModel):
    name: str
    
class CategoryUpdateDTO(BaseModel):
    name: str | None = None