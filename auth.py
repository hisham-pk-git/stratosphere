from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models import User  
from database import get_db  
from passlib.context import CryptContext
from typing import Any, Annotated
from schemas import UserCreate

# Constants for JWT
SECRET_KEY = "123456789101112"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 Bearer Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Hashing the password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Method to verify the password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Create access token
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print("Token created:", token)  # Add logging
    return token


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("Payload:", payload)  # Add logging
        username = payload.get("username")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError as e:
        print("JWTError:", e)  # Add logging
        raise HTTPException(status_code=401, detail="Invalid token")
    
def get_admin_user(current_user: Annotated[UserCreate, Depends(get_current_user)]):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
#     print("inside get_current_user:" + token)
#     try:
#         print("inside try payload:" + token)
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         if username is None:
#             raise HTTPException(status_code=401, detail="Invalid token")
#         user = db.query(User).filter(User.username == username).first()
#         if not user:
#             raise HTTPException(status_code=401, detail="User not found")
#         return user
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")

# # Role-based access control for admin
# def admin_required(current_user: User = Depends(get_current_user)) -> User:
#     print("inside admin_required")
#     if current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="Admin access required")
#     return current_user
