from fastapi import FastAPI, Depends, Request, Form, status

from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from routers import *
import schema
import models
from database import SessionLocal, engine
import crud
from datetime import datetime

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.mount("/templates", StaticFiles(directory="templates"), name="templates")


# region LOGIN
@app.get("/")
def login(request: Request, db: Session = Depends(get_db)):
    todos = db.query(models.Todo).all()
    return templates.TemplateResponse("backend/login.html", {"request": request, "todo_list": todos})

# endregion

# region HOME DASHBOARD
@app.get("/home")
def home(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("backend/index.html", {"request": request})

@app.get("/auth")
def auth(request: Request, db: Session = Depends(get_db)):
    # username = db.query(models.User).filter(models.User.username == username).first()
    # password = db.query(models.User).filter(models.User.password == password).first()
    url = app.url_path_for("home")
    return RedirectResponse(url=url)#, status_code=status.HTTP_303_SEE_OTHER)
# endregion

# region PRODUCTS


@app.get("/list_products")
def list_products(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("backend/page-list-product.html", {"request": request})


@app.get("/add_product")
def add_product(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("backend/page-add-product.html", {"request": request})

# endregion

# region CATEGORIES


@app.get("/list_categories")
def list_categories(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("backend/page-list-category.html", {"request": request})


@app.get("/add_category")
def add_product(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("backend/page-add-category.html", {"request": request})

# endregion

# region SALES


@app.get("/list_sales")
def list_sales(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("backend/page-list-sale.html", {"request": request})


@app.get("/add_sale")
def add_product(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("backend/page-add-sale.html", {"request": request})
# endregion

# region PURCHASES


@app.get("/list_puchases")
def list_puchases(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("backend/page-list-purchase.html", {"request": request})


@app.get("/add_purchase")
def add_product(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("backend/page-add-purchase.html", {"request": request})

# endregion

# region RETURNS


@app.get("/list_returns")
def list_returns(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("backend/page-list-returns.html", {"request": request})


@app.get("/add_return")
def add_return(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("backend/page-add-return.html", {"request": request})
# endregion

# region USERS

@app.get("/list_users")
def list_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return templates.TemplateResponse("backend/page-list-users.html", {"request": request, "user_list": users})

@app.get("/add_user_page")
def add_user_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("backend/page-add-user.html", {"request": request})

@app.get("/find_username/{username}")
async def find_username(username:str,request: Request, db: Session = Depends(get_db)):
    username = db.query(models.User).filter(models.User.username == username).first()
    msg=""
    if not username:
        msg="notfound"
    else:
        msg="exists"
    return msg

@app.get("/find_staffcode/{staff_code}")
async def find_staffcode(staff_code:str,request: Request, db: Session = Depends(get_db)):
    staff_code = db.query(models.User).filter(models.User.staff_code == staff_code).first()
    msg=""
    if not staff_code:
        msg="notfound"
    else:
        msg="exists"
    return msg


@app.post("/create_user")
def create_user(request: Request, name: str = Form(...),staff_code:str=Form(...),username:str=Form(...), password: str = Form(...),role:str=Form(...), db: Session = Depends(get_db)):
    new_user = models.User(name=name,staff_code=staff_code,username=username,password=password,role=role)
    db.add(new_user)
    db.commit()
    url = app.url_path_for("list_users")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

@app.get("/delete_user/{user_id}")
def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    db.delete(user)
    db.commit()
    url = app.url_path_for("list_users")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)
# endregion
# region OLD


    


