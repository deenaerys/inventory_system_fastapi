from datetime import date
from pydantic import BaseModel
class Movie(BaseModel):
    id = int
    title = str
    complete = bool
    

    class Config:
        orm_mode = True