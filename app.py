from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Plan, User, PlanPermission, Permission
from schemas import PlanResponse, UserCreate, UserResponse, PlanUpdateResponse, PermissionRes, PermissionResponse
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
async def get_plans(db: Session = Depends(get_db)) -> Any:
    return db.query(Plan).all()

@app.post("/create-plan", response_model=PlanResponse, dependencies=[Depends(get_admin_user)])
async def create_plan(planres: PlanResponse, db: Session = Depends(get_db)) -> Any:
    plan = Plan(name=planres.name, description=planres.description, usage_limit=planres.usage_limit)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

@app.put("/update-plan/{plan_id}", response_model=PlanUpdateResponse, dependencies=[Depends(get_admin_user)])
async def update_plan(plan_id: int, planres: PlanResponse, db: Session = Depends(get_db)) -> Any:
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if planres.name != "string" and planres.name != plan.name:
        plan.name = planres.name
    if planres.description != "string" and planres.description != plan.description:
        plan.description = planres.description
    if planres.usage_limit != 0 and planres.usage_limit != plan.usage_limit:
        plan.usage_limit = planres.usage_limit
    db.commit()
    db.refresh(plan)
    return PlanUpdateResponse(message="Plan updated successfully", plan=plan)

@app.delete("/delete-plan/{plan_id}", dependencies=[Depends(get_admin_user)])
async def delete_plan(plan_id: int, db: Session = Depends(get_db)) -> Any:
    plan_permission = db.query(PlanPermission).filter(PlanPermission.plan_id == plan_id).all()
    if plan_permission:
        for permission in plan_permission:
            print("Permission:", permission.id)  # Add logging
            db.delete(permission)
        db.commit()
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(plan)
    db.commit()
    return {"message": "Plan deleted successfully"}

@app.get("/permissions", response_model=List[PermissionRes], dependencies=[Depends(get_admin_user)])
async def get_permissions(db: Session = Depends(get_db)) -> Any:
    return db.query(Permission).all()

@app.post("/create-permission", response_model=PermissionResponse, dependencies=[Depends(get_admin_user)])
async def create_permission(permission: PermissionRes, db: Session = Depends(get_db)) -> Any:
    permission = Permission(name=permission.name, api_endpoint=permission.api_endpoint, description=permission.description)
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return PermissionResponse(message="Permission created successfully", permission=permission)

@app.put("/update-permission/{permission_id}", response_model=PermissionResponse, dependencies=[Depends(get_admin_user)])
async def update_permission(permission_id: int, permission: PermissionRes, db: Session = Depends(get_db)) -> Any:
    permissiondb = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    if permission.name != "string" and permission.name != permissiondb.name:
        permissiondb.name = permission.name
    if permission.api_endpoint != "string" and permission.api_endpoint != permissiondb.api_endpoint:
        permissiondb.api_endpoint = permission.api_endpoint
    if permission.description != "string" and permission.description != permissiondb.description:
        permissiondb.description = permission.description
    db.commit()
    db.refresh(permissiondb)
    return PermissionResponse(message="Permission updated successfully", permission=permissiondb)

@app.delete("/delete-permission/{permission_id}", dependencies=[Depends(get_admin_user)])
async def delete_permission(permission_id: int, db: Session = Depends(get_db)) -> Any:
    plan_permission = db.query(PlanPermission).filter(PlanPermission.api_id == permission_id).all()
    if plan_permission:
        for permission in plan_permission:
            print("Permission:", permission.id)
            db.delete(permission)
        db.commit()
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    db.delete(permission)
    db.commit()
    return {"message": "Permission deleted successfully"}
