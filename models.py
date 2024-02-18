# schemas.py

from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    is_active: bool = True
    role: str = "user" 

class UserRead(BaseModel):
    id: int
    username: str
    is_active: bool
    role: str

    class Config:
        orm_mode = True

class QuizCreate(BaseModel):
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str

class QuizRead(BaseModel):
    id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str

    class Config:
        orm_mode = True
