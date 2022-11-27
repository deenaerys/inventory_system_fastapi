from pydantic import BaseModel
from datetime import datetime
from typing import Optional
class Movie(BaseModel):
    id = int
    title = str
    complete = bool
    
    class Config:
        orm_mode = True

class User(BaseModel):    
    name=str
    username=str    
    staff_code=str
    status = bool
    enroll_time = datetime
    last_login=datetime
    role = str
    
    class Config:
        orm_mode: True

class UserCreate(User):
    password: str
class User(User):
    id: int         