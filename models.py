from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

#sqlalchemy models ORM
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    password = Column(String)
    role = Column(String)

class Plan(Base):
    __tablename__ = "plan"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    usage_limit = Column(Integer)

class Permission(Base):
    __tablename__ = "endpoints"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    endpoint = Column(String)
    description = Column(String)
    
class Subscription(Base):
    __tablename__ = "subscription"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan_id = Column(Integer, ForeignKey("plan.id"))
    usage = Column(Integer)
    
class PlanPermission(Base):
    __tablename__ = "plan_endpoints"
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plan.id"))
    api_id = Column(Integer, ForeignKey("endpoints.id"))
    
