from fastapi import APIRouter, Depends
from utility import check_access_and_usage, increment_usage
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/cloud-services")

# 1. Storage Bucket: Create a new storage bucket
@router.post("/create-bucket", dependencies=[Depends(get_current_user)])
def create_bucket(user_id: int, db: Session = Depends(get_db)):
    check_access_and_usage(user_id, "/create-bucket", db)
    # Simulate bucket creation logic here (e.g., adding to database, etc.)
    increment_usage(user_id, db)
    return {"message": "Bucket created successfully"}

# 2. Storage Bucket: View an existing storage bucket
@router.get("/get-bucket", dependencies=[Depends(get_current_user)])
def get_bucket(user_id: int, db: Session = Depends(get_db)):
    check_access_and_usage(user_id, "/get-bucket", db)
    # Simulate bucket retrieval logic
    increment_usage(user_id, db)
    return {"message": "Bucket details fetched successfully"}

# 3. Storage Bucket: Delete a storage bucket
@router.delete("/delete-bucket", dependencies=[Depends(get_current_user)])
def delete_bucket(user_id: int, db: Session = Depends(get_db)):
    check_access_and_usage(user_id, "/delete-bucket", db)
    # Simulate bucket deletion logic
    increment_usage(user_id, db)
    return {"message": "Bucket deleted successfully"}

# 4. Virtual Machine: Create a new virtual machine
@router.post("/create-vm", dependencies=[Depends(get_current_user)])
def create_vm(user_id: int, db: Session = Depends(get_db)):
    check_access_and_usage(user_id, "/create-vm", db)
    # Simulate VM creation logic
    increment_usage(user_id, db)
    return {"message": "Virtual machine created successfully"}

# 5. Virtual Machine: View details of an existing virtual machine
@router.get("/get-vm", dependencies=[Depends(get_current_user)])
def get_vm(user_id: int, db: Session = Depends(get_db)):
    check_access_and_usage(user_id, "/get-vm", db)
    # Simulate VM retrieval logic
    increment_usage(user_id, db)
    return {"message": "Details of virtual machine fetched successfully"}

# 6. Virtual Machine: Delete an existing virtual machine
@router.delete("/delete-vm", dependencies=[Depends(get_current_user)])
def delete_vm(user_id: int, db: Session = Depends(get_db)):
    check_access_and_usage(user_id, "/delete-vm", db)
    # Simulate VM deletion logic
    increment_usage(user_id, db)
    return {"message": "Virtual machine deleted successfully."}

# 7. Logs: Create a new log file
@router.post("/create-logs", dependencies=[Depends(get_current_user)])
def create_logs(user_id: int, db: Session = Depends(get_db)):
    check_access_and_usage(user_id, "/create-logs", db)
    # Simulate log creation logic
    increment_usage(user_id, db)
    return {"message": "Log file created successfully."}

# 8. Logs: View an existing log file
@router.get("/get-logs", dependencies=[Depends(get_current_user)])
def get_logs(user_id: int, db: Session = Depends(get_db)):
    check_access_and_usage(user_id, "/get-logs", db)
    # Simulate log retrieval logic
    increment_usage(user_id, db)
    return {"message": "Details of log file fetched successfully"}

# 9. Logs: Delete an existing log file
@router.delete("/delete-logs", dependencies=[Depends(get_current_user)])
def delete_logs(user_id: int, db: Session = Depends(get_db)):
    check_access_and_usage(user_id, "/delete-logs", db)
    # Simulate log deletion logic
    increment_usage(user_id, db)
    return {"message": "Log file deleted successfully."}
