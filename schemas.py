from pydantic import BaseModel

class PlanResponse(BaseModel):
    id: int
    name: str
    description: str
    usage_limit: int
    
    class Config:
        from_attributes  = True
        

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class UserResponse(BaseModel):
    username: str
    role: str

    class Config:
        from_attributes = True