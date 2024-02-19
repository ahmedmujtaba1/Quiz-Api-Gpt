from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional
from pydantic import BaseModel
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Models
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    hashed_password: str
    is_active: bool = True
    role: str = Field(default="user")

class Quiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str

# Schemas
class UserCreate(BaseModel):
    username: str
    password: str
    is_active: bool = True
    role: str = "user"

class UserAuth(BaseModel):
    username: str
    password: str

class QuizCreate(BaseModel):
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str

# FastAPI app
app = FastAPI()

# Database utility function
def get_db():
    with Session(engine) as session:
        yield session

# Create database tables
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# Authentication function
def authenticate_user(db: Session, username: str, password: str):
    user = db.exec(select(User).where(User.username == username)).first()
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

# User management endpoint
@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.exec(select(User).where(User.username == user.username)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, is_active=user.is_active, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully"}

# Quiz management endpoint with authentication and role check
@app.post("/quizzes/", status_code=status.HTTP_201_CREATED)
def create_quiz(quiz: QuizCreate, credentials: UserAuth, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add quizzes")
    db_quiz = Quiz(**quiz.dict())
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return {"message": "Quiz added successfully"}
