from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Plan, User, PlanPermission, Permission, Subscription
from schemas import PlanResponse, UserCreate, UserResponse, PlanUpdateResponse, PermissionRes, PermissionResponse, PlanDetails, SubscriptionCreate, SubscriptionResponse, UsageResponse, AccessControlResponse
from typing import Any, Annotated, List
from passlib.context import CryptContext
from cloud_services import router as cloud_services_router
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
app.include_router(cloud_services_router)

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

@app.get("/plans", response_model=List[PlanDetails])
async def get_plans(db: Session = Depends(get_db)) -> Any:
    plans = db.query(Plan).all()
    plan_details = []
    for plan in plans:
        plan_permission = db.query(PlanPermission).filter(PlanPermission.plan_id == plan.id).all()
        permission_list = []
        for permission in plan_permission:
            permission_list.append(db.query(Permission).filter(Permission.id == permission.api_id).first().api_endpoint)
        plan_details.append(PlanDetails(id=plan.id, name=plan.name, description=plan.description, usage_limit=plan.usage_limit, endpoints=permission_list))
    return plan_details

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


# --------User Subscription Handling-----!!

# POST /subscriptions (Create a Subscription)
@app.post("/subscriptions", response_model=SubscriptionResponse, dependencies=[Depends(get_current_user)])
async def create_subscription(subscription_data: SubscriptionCreate, db: Session = Depends(get_db)):
    # Validate user existence
    user = db.query(User).filter(User.id == subscription_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate plan existence
    plan = db.query(Plan).filter(Plan.id == subscription_data.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Check if user already has a subscription
    existing_subscription = db.query(Subscription).filter(Subscription.user_id == subscription_data.user_id).first()
    if existing_subscription:
        raise HTTPException(status_code=400, detail="User already subscribed to a plan")

    # Create new subscription
    new_subscription = Subscription(user_id=subscription_data.user_id, plan_id=subscription_data.plan_id, usage=0)
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)

    return SubscriptionResponse(
        user_id=new_subscription.user_id,
        plan_id=new_subscription.plan_id,
        usage=new_subscription.usage
    )

# GET /subscriptions/{userId}
@app.get("/subscriptions/{user_id}", response_model=SubscriptionResponse, dependencies=[Depends(get_current_user)])
def get_subscription(user_id: int, db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return SubscriptionResponse(
        user_id=subscription.user_id,
        plan_id=subscription.plan_id,
        usage=subscription.usage
    )

# GET /subscriptions/{userId}/usage
@app.get("/subscriptions/{user_id}/usage", response_model=UsageResponse, dependencies=[Depends(get_current_user)])
def get_subscription_usage(user_id: int, db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return UsageResponse(
        user_id=subscription.user_id,
        usage=subscription.usage
    )

# Assign/Modify User Plan
@app.put("/subscriptions/{user_id}/{plan_id}", response_model=SubscriptionResponse, dependencies=[Depends(get_admin_user)])
def update_subscription(user_id: int, plan_id: int, db: Session = Depends(get_db)):
    # Fetch the user's subscription
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Validate new plan existence
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Update the subscription
    subscription.plan_id = plan_id
    db.commit()
    db.refresh(subscription)

    return SubscriptionResponse(
        user_id=subscription.user_id,
        plan_id=subscription.plan_id,
        usage=subscription.usage
    )

# ----Access Control---!!

# Return the number of api requests made by the user by including the plan details. 
@app.get("/access/{user_id}/{api_request}", response_model=AccessControlResponse)
def check_access_permission(user_id: int, api_request: str, db: Session = Depends(get_db)):
    # Fetch the user's subscription
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found for the user")

    # Fetch the plan details
    plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found for the subscription")

    # Fetch the allowed endpoints for the plan
    allowed_endpoints = db.query(Permission).join(PlanPermission, Permission.id == PlanPermission.api_id) \
                        .filter(PlanPermission.plan_id == subscription.plan_id).all()
    
    # Check if the requested API is within the allowed endpoints
    endpoint_match = next((ep for ep in allowed_endpoints if ep.api_endpoint.strip("/") in api_request), None)

    # Determine access status
    access_status = "You have access to this endpoint" if endpoint_match else "You don't have access to this endpoint"

    # Prepare response using the AccessControlResponse model
    response = AccessControlResponse(
        access_status=access_status,
        plan_name=plan.name,
        plan_description=plan.description,
        accessible_endpoints=[{"name": ep.name, "endpoint": ep.api_endpoint} for ep in allowed_endpoints]
    )
    return response

# ---Usage Tracking ---!!

# Return the plan limit subscribed by the user along with how mumanych attempts left for the user.
@app.get("/usage/{user_id}")
def track_api_request(user_id: int, db: Session = Depends(get_db)):
    # Fetch the user's subscription
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found for the user")

    # Fetch the plan details
    plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found for the subscription")
    
    # Calculate remaining attempts (if usage limit is not unlimited)
    if plan.usage_limit != 0:
        remaining_attempts = plan.usage_limit - subscription.usage
    else:
        remaining_attempts = "Unlimited"  # If the plan has unlimited usage

    # Return the number of API requests made by the user and the plan details
    response = {
        "user_id": user_id,
        "api_request_count": subscription.usage, 
        "plan_name": plan.name,
        "plan_description": plan.description,
        "usage_limit": plan.usage_limit,
        "remaining_attempts": remaining_attempts
    }
    
    return response


