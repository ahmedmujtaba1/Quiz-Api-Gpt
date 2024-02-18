from pydantic import BaseModel

class QuizBase(BaseModel):
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str

class QuizCreate(QuizBase):
    correct_option: str

class Quiz(QuizBase):
    id: int
    correct_option: str

    class Config:
        orm_mode = True
