from fastapi import HTTPException
from models import Subscription
from sqlalchemy.orm import Session
from models import Plan, Permission, PlanPermission


# ----Access Control----!!

# Function to check access and usage
def check_access_and_usage(user_id: int, api_endpoint: str, db: Session):
    # Retrieve subscription and plan
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Check usage limit
    if plan.usage_limit != 0 and subscription.usage >= plan.usage_limit:
        raise HTTPException(
            status_code=403, 
            detail="Usage limit exceeded. Upgrade your plan to continue accessing this API."
        )
    
    # Check if the user has access to the requested API
    allowed_endpoints = db.query(Permission.api_endpoint).join(
        PlanPermission, Permission.id == PlanPermission.api_id
    ).filter(PlanPermission.plan_id == subscription.plan_id).all()
    
    allowed_endpoints = [endpoint.api_endpoint for endpoint in allowed_endpoints]
    if api_endpoint not in allowed_endpoints:
        raise HTTPException(
            status_code=403, 
            detail="You do not have access to this endpoint with your current plan."
        )
    
    return

# Function to increment usage
def increment_usage(user_id: int, db: Session):
    subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    if subscription:
        subscription.usage += 1  # Increment usage count
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Subscription not found")