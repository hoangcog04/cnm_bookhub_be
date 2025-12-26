from pydantic import BaseModel, ConfigDict

class ProvinceDTO(BaseModel):
    code: str
    full_name : str
    
    model_config = ConfigDict(from_attributes=True)
    