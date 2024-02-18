from pydantic import BaseModel

class QuizCreate(BaseModel):
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str

class Quiz(QuizCreate):
    id: int

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    is_active: bool

    class Config:
        orm_mode = True
