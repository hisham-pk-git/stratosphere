from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# Database configuration
DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/stratosphere"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Asynchronous database configuration
ASYNC_DATABASE_URL = "mysql+aiomysql://root:root@localhost:3306/stratosphere"
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency for asynchronous session (only for specific use cases)
async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session        