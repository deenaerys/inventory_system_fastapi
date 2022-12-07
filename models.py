from sqlalchemy import BIGINT, Boolean, Column, Integer, String, DateTime
from datetime import datetime
from database import Base


# region USER
class User(Base):
    __tablename__ = "tblusers"
    id = Column(BIGINT, primary_key=True, index=True,
                autoincrement=True, nullable=False)
    name = Column(String(255))
    username = Column(String(255))
    password = Column(String(255))
    staff_code = Column(String(255))
    status = Column(Boolean, default=True)
    enroll_time = Column(DateTime, default=datetime.now())
    last_login = Column(DateTime, default=datetime.now())
    role = Column(String(255), default="admin")
# endregion

# region CATEGORY
class Category(Base):
    __tablename__ = "tblcategories"
    id = Column(BIGINT, primary_key=True, index=True,
                autoincrement=True, nullable=False)
    category = Column(String(255))
    create_time = Column(DateTime, default=datetime.now())
    created_by = Column(String(255))
# endregion

# region BRAND
class Brand(Base):
    __tablename__ = "tblbrands"
    id = Column(BIGINT, primary_key=True, index=True,
                autoincrement=True, nullable=False)
    brand = Column(String(255))
    create_time = Column(DateTime, default=datetime.now())
    created_by = Column(String(255))
# endregion


# region OLDCODE
class Todo(Base):
    __tablename__ = "todos"

    id = Column(BIGINT, primary_key=True, index=True)
    title = Column(String(255))
    complete = Column(Boolean, default=False)
# endregion
