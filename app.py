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
    return templates.TemplateResponse("backend/login.html", {"request": request})
@app.get("/login")
def login(request: Request, db: Session = Depends(get_db)):    
    return templates.TemplateResponse("backend/login.html", {"request": request})

@app.get("/signout/{user_id}")
def signout(request: Request,user_id=int, db: Session = Depends(get_db)):
    print('signout ',user_id)
    user=db.query(models.User).get(user_id)  
    print('signout ',user.id)
    user.last_login=datetime.now()
    db.commit()
    db.close()
    url = app.url_path_for("login")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)
# endregion

# region HOME DASHBOARD
@app.post("/home")
def auth(request: Request,username:str= Form(...),password:str=Form(...), db: Session = Depends(get_db)):        
    d_username=db.query(models.User).filter(models.User.username == username).first()
    db.close()
   

    if d_username:
        print('USERNAME FOUND')
        
        if d_username.password==password:
            context={"request": request,
                    "greetings":"Hello, " + d_username.name,
                    "last_login":"Your last session was on "+ d_username.last_login.strftime("%A %b. %d, %Y at %I:%M %p "),
                    "name":d_username.name,
                    "username":d_username.username,
                    "user_id":d_username.id,
                    "role":d_username.role}           
            return templates.TemplateResponse("backend/index.html", context)
        
        else:
            print('Wrong Password')
            return templates.TemplateResponse("backend/login.html",{"request":request,"error":"Invalid Username/Password"})
    else:
        print("USERNAME NOT FOUND")
        return templates.TemplateResponse("backend/login.html",{"request":request,"error":"Invalid Username/Password"})

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
    categories = db.query(models.Category).all()
    return templates.TemplateResponse("backend/page-list-category.html", {"request": request,"category_list":categories})


@app.get("/add_category")
def add_product(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("backend/page-add-category.html", {"request": request})

@app.get("/find_category/{category}")
async def find_category(category:str,request: Request, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.category == category).first()
    msg=""
    if not category:
        msg="notfound"
    else:
        msg="exists"
    return msg

@app.post("/create_category")
def create_category(request: Request, category: str = Form(...),created_by=Form(...), db: Session = Depends(get_db)):
    created_by=created_by
    print('created_by' ,created_by)
    new_category = models.Category(category=category,created_by=created_by)
    db.add(new_category)
    db.commit()
    db.close()        
    url = app.url_path_for("list_categories")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

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

@app.get("/get_user/{user_id}")
def get_user(user_id:int,request:Request,db:Session=Depends(get_db)):
    user=db.query(models.User).get(user_id)    
    return templates.TemplateResponse("backend/page-edit-user.html", {"request": request,"userid":user.id,"name":user.name,"staff_code":user.staff_code,"username":user.username,"password":user.password,"role":user.role})

@app.post("/create_user")
def create_user(request: Request, name: str = Form(...),staff_code:str=Form(...),username:str=Form(...), password: str = Form(...),role:str=Form(...), db: Session = Depends(get_db)):
    new_user = models.User(name=name,staff_code=staff_code,username=username,password=password,role=role)
    db.add(new_user)
    db.commit()
    db.close()        
    url = app.url_path_for("list_users")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

@app.get("/delete_user/{user_id}")
def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    db.delete(user)
    db.commit()
    db.close()
    url = app.url_path_for("list_users")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)

@app.post("/update_user/{user_id}")
def update_user(request:Request,user_id:int,name: str = Form(...),staff_code:str=Form(...),username:str=Form(...), password: str = Form(...),role:str=Form(...),db:Session=Depends(get_db)):
    user=db.query(models.User).get(user_id)
    print('user',user.name)
    
    if user:       
        user.name=name
        user.staff_code=staff_code
        user.usernamae=username
        user.password=password
        user.role=role
        db.commit()
   
    db.close()
    url = app.url_path_for("list_users")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)



# endregion


