from sqlmodel import Session, select
from app.models.models import Quiz

def create_quiz(db: Session, quiz: Quiz) -> Quiz:
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz

def get_quiz(db: Session, quiz_id: int) -> Quiz:
    return db.get(Quiz, quiz_id)
