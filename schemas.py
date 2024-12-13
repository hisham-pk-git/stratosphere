from pydantic import BaseModel

#pydantic models used to validate request and send response data 
class PlanResponse(BaseModel):
    id: int
    name: str
    description: str
    usage_limit: int
    
    class Config:
        from_attributes  = True
        
class PlanDetails(BaseModel):
    id: int
    name: str
    description: str
    endpoints: list
    usage_limit: int
        

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    username: str
    role: str

    class Config:
        from_attributes = True
        
class PlanUpdateResponse(BaseModel):
    message: str
    plan: PlanResponse
    
class PermissionRes(BaseModel):
    id: int
    name: str
    api_endpoint: str
    description: str
    class Config:
        from_attributes  = True
    
class PermissionResponse(BaseModel):
    message: str
    permission: PermissionRes
        
