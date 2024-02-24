from fastapi import FastAPI, Depends, HTTPException, Response, status, Cookie
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional
from pydantic import BaseModel
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
import aiosmtplib
from email.message import EmailMessage

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
engine = create_engine(DATABASE_URL)

app = FastAPI()

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    email: str = Field(index=True)
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    role: str = Field(default="user")

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserAuth(BaseModel):
    username: str
    password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as session:
        yield session

async def send_verification_email(email: str, username: str):
    verification_link = f"http://localhost:8000/verify/{username}"
    message = EmailMessage()
    message["From"] = EMAIL_USER
    message["To"] = email
    message["Subject"] = "Verify your email for FastAPI App"
    message.set_content(f"Thank you for signing up. Please click the following link to verify your email: {verification_link}")
    await aiosmtplib.send(message, hostname="smtp.gmail.com", port=587, start_tls=True, username=EMAIL_USER, password=EMAIL_PASSWORD)

@app.post("/signup/")
async def signup(user_create: UserCreate, db: Session = Depends(get_db)):
    try:
        user = db.exec(select(User).where(User.username == user_create.username)).first()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_password = pwd_context.hash(user_create.password)
    user = User(username=user_create.username, email=user_create.email, hashed_password=hashed_password, is_active=True, is_verified=False)
    db.add(user)
    db.commit()
    await send_verification_email(user_create.email, user_create.username)
    return {"message": "User created successfully, please check your email to verify your account."}

@app.get("/verify/{username}")
def verify_email(username: str, db: Session = Depends(get_db)):
    user = db.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = True
    db.add(user)
    db.commit()
    return {"message": "User verified successfully"}

@app.post("/login/")
def login(credentials: HTTPBasicCredentials, response: Response, db: Session = Depends(get_db)):
    user = db.exec(select(User).where(User.username == credentials.username)).first()
    if not user or not pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not verified")
    session_token = f"{user.username}:{pwd_context.hash(credentials.password)}"
    response.set_cookie(key="session_token", value=session_token, httponly=True, expires=7200)  # 2 hours
    return {"message": "Login successful"}

# Add other endpoints as needed

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
