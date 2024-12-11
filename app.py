from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Plan, User
from schemas import PlanResponse, UserCreate, UserResponse
from typing import Any
from passlib.context import CryptContext


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    

@app.post("/login")
async def login_user():
    pass 

@app.get("/plans")
async def get_plans(db: Session = Depends(get_db)):
    return db.query(Plan).all()

@app.post("/create-plan", response_model=PlanResponse)
async def create_plan(planres: PlanResponse, db: Session = Depends(get_db)) -> Any:
    plan = Plan(name=planres.name, description=planres.description, usage_limit=planres.usage_limit)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

