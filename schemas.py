from pydantic import BaseModel

class PlanResponse(BaseModel):
    id: int
    name: str
    description: str
    usage_limit: int
    
    class Config:
        orm_mode = True