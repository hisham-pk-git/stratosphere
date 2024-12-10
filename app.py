from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Plan
from schemas import PlanResponse
from typing import Any

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

@app.get("/") 
def read_root():
    return {"Hello": "World"}

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

