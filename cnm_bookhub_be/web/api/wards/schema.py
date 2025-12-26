from pydantic import BaseModel, ConfigDict

class WardDTO(BaseModel):
    code: str
    province_code: str
    full_name: str
    
    model_config = ConfigDict(from_attributes=True)