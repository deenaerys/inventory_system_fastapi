from sqlalchemy.orm import Session
from models import *

def create_user(db:Session, name,username, password, staff_code,status,enroll_time,last_login,role):
    new_user = User(name=name,username=username, password=password, staff_code=staff_code,status=status,enroll_time=enroll_time,last_login=last_login,role=role)
    db.add(new_user)    
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user(db:Session, id:int):
    db_user = db.query(User).filter(User.id==id).first()
    return db_user

def list_users(db:Session):   
    all_users = db.query(User).all()
    return all_users


def update_friend(db:Session, name=str,username=str, password=str, staff_code=str,status=bool,role=str):
    db_user = get_user(db=db, id=id)
    db_user.name = name
    db_user.username = username
    db_user.password = password
    db_user.staff_code=staff_code
    db_user.status=status
    db_user.role=role
    db.commit()
    db.refresh(db_user) 
    return db_user

def delete_user(db:Session, id:int):
   db_user = get_user(db=db, id=id)
   db.delete(db_user)
   db.commit() 