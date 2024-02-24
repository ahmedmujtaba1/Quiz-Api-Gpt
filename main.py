from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, Response, Cookie
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional
from pydantic import BaseModel
from passlib.context import CryptContext
from dotenv import load_dotenv
import os, aiosmtplib
from email.message import EmailMessage

# Initialize environment and security
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define models
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

# Define schemas
class UserCreate(BaseModel):
    username: str
    password: str
    is_active: bool = True
    role: str = "user"

class QuizCreate(BaseModel):
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str

app = FastAPI()

# Database utility
def get_db():
    with Session(engine) as session:
        yield session

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

def authenticate_user(db: Session, username: str, password: str):
    user = db.exec(select(User).where(User.username == username)).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        return False
    return user

async def send_verification_email(email: str):
    message = EmailMessage()
    message["From"] = EMAIL_USER
    message["To"] = email
    message["Subject"] = "Verify your email"
    message.set_content("Thank you for signing up. Please verify your email address.")

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=EMAIL_USER,
        password=EMAIL_PASSWORD
    )
@app.post("/login/")
def login(response: Response, username: str, password: str, db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    # Session token is a combination of username and hashed password
    session_token = f"{username}:{user.hashed_password}"
    response.set_cookie(key="session_token", value=session_token, httponly=True, expires=7200)  # 2 hours
    return {"message": "Login successful"}

@app.post("/logout/")
def logout(response: Response):
    response.delete_cookie("session_token")
    return {"message": "Logged out successfully"}

def get_current_user(session_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    if session_token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    username, hashed_password = session_token.split(":")
    user = db.exec(select(User).where(User.username == username)).first()
    if not user or user.hashed_password != hashed_password:
        raise HTTPException(status_code=401, detail="Invalid session token")
    return user

@app.post("/quizzes/", response_model=QuizCreate)
def create_quiz(quiz: QuizCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    db_quiz = Quiz(**quiz.dict())
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz
