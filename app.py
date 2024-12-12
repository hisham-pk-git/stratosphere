from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Plan, User
from schemas import PlanResponse, UserCreate, UserResponse
from typing import Any, Annotated, List
from passlib.context import CryptContext
from database import get_db
from auth import (
    create_access_token,
    hash_password,
    verify_password,
    get_current_user,
    # admin_required,
    oauth2_scheme,
    get_admin_user
)


app = FastAPI()

@app.post("/register", response_model=UserResponse) 
async def register_user(newUser: UserCreate, db: Session = Depends(get_db)) -> Any:
    # Check if the username already exists
    existing_user = db.query(User).filter(User.username == newUser.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash the password
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    hashed_password = pwd_context.hash(newUser.password)
    user = User(username=newUser.username, password=hashed_password, role=newUser.role)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse(message="User created successfully", username=newUser.username, role=newUser.role)

@app.post("/token")
def login(formdata: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    print("formdata:" + str(formdata.username) + " " + str(formdata.password))  # Add logging
    user = db.query(User).filter(User.username == formdata.username).first()
    if not user or not verify_password(formdata.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Include role in the token payload
    access_token = create_access_token({"username": user.username, "role": user.role})
    print("Access token:", access_token)  # Add logging
    return {"access_token": access_token, "token_type": "bearer"}   

@app.get("/plans", response_model=List[PlanResponse])
async def get_plans(token: Annotated[str, Depends(get_admin_user)], db: Session = Depends(get_db)) -> Any:
    return db.query(Plan).all()

@app.post("/create-plan", response_model=PlanResponse, dependencies=[Depends(get_admin_user)])
async def create_plan(planres: PlanResponse, db: Session = Depends(get_db)) -> Any:
    plan = Plan(name=planres.name, description=planres.description, usage_limit=planres.usage_limit)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan
