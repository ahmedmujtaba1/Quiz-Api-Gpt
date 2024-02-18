from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session
from . import models, schemas, crud
from app.models import *
from .database import engine, DATABASE_URL
from typing import List

models.SQLModel.metadata.create_all(engine)

app = FastAPI()

def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()

@app.post("/quizzes/", response_model=schemas.Quiz)
def create_quiz(quiz: schemas.QuizCreate, db: Session = Depends(get_db)):
    return crud.create_quiz(db=db, quiz=quiz)

@app.get("/quizzes/{quiz_id}", response_model=schemas.Quiz)
def read_quiz(quiz_id: int, db: Session = Depends(get_db)):
    db_quiz = crud.get_quiz(db, quiz_id=quiz_id)
    if db_quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return db_quiz
