from sqlmodel import SQLModel, Field
from typing import Optional

class Quiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    hashed_password: str
    is_active: bool = True
