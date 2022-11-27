from sqlalchemy import BIGINT,Boolean, Column, Integer, String,DateTime
from datetime import datetime
from database import Base


class Todo(Base):
    __tablename__ = "todos"

    id = Column(BIGINT, primary_key=True, index=True)
    title = Column(String(255))
    complete = Column(Boolean, default=False)


class User(Base):
    __tablename__ = "tblusers"
    id = Column(BIGINT, primary_key=True, index=True, autoincrement=True, nullable=False)
    name=Column(String(255))
    username=Column(String(255))
    password=Column(String(255))
    staff_code=Column(String(255))
    status = Column(Boolean, default=True)
    enroll_time = Column(DateTime, default=datetime.now())
    last_login=Column(DateTime,default=datetime.now())
    role = Column(String(255), default="admin")