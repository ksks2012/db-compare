from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

import uvicorn
import os
import argparse

# Load environment variables
load_dotenv()

# FastAPI application
app = FastAPI()

# Database connection settings
MYSQL_URL = os.getenv("MYSQL_DATABASE_URL")
POSTGRES_URL = os.getenv("POSTGRES_DATABASE_URL")

# SQLAlchemy setup
Base = declarative_base()

# MySQL engine and session
mysql_engine = create_engine(MYSQL_URL)
MysqlSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mysql_engine)

# PostgreSQL engine and session
postgres_engine = create_engine(POSTGRES_URL)
PostgresSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=postgres_engine)

# Define User model (SQLAlchemy)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    email = Column(String(100), unique=True, index=True)

# Create tables
Base.metadata.create_all(bind=mysql_engine)
Base.metadata.create_all(bind=postgres_engine)

# Pydantic models (for API input/output)
class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True

# Helper function: select database
def get_db(db_type: str):
    if db_type == "mysql":
        db = MysqlSessionLocal()
    elif db_type == "postgres":
        db = PostgresSessionLocal()
    else:
        raise ValueError("Invalid database type")
    try:
        yield db
    finally:
        db.close()

# CRUD operations
@app.post("/users/{db_type}", response_model=UserResponse)
async def create_user(db_type: str, user: UserCreate):
    if db_type not in ["mysql", "postgres"]:
        raise HTTPException(status_code=400, detail="Invalid database type")
    
    db = next(get_db(db_type))
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{db_type}/{user_id}", response_model=UserResponse)
async def read_user(db_type: str, user_id: int):
    if db_type not in ["mysql", "postgres"]:
        raise HTTPException(status_code=400, detail="Invalid database type")
    
    db = next(get_db(db_type))
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Start application
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run FastAPI app with configurable host and port.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)
