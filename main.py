from fastapi import FastAPI, Depends
from sqlmodel import Session, SQLModel, create_engine
from models import Quiz, User
from schemas import QuizCreate, UserCreate, UserRead
from database import engine
from crud import create_quiz, get_quiz, create_user, verify_user
import crud 

app = FastAPI()

# Create database tables
SQLModel.metadata.create_all(engine)

@app.post("/quizzes/", response_model=Quiz)
def add_quiz(quiz: QuizCreate, db: Session = Depends(crud.get_db)):
    return crud.create_quiz(db=db, quiz=quiz)

@app.get("/quizzes/{quiz_id}", response_model=Quiz)
def read_quiz(quiz_id: int, db: Session = Depends(crud.get_db)):
    return crud.get_quiz(db=db, quiz_id=quiz_id)

# Add user authentication endpoints
