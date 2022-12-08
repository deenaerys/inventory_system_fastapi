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
from starlette.middleware.sessions import SessionMiddleware

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

app = FastAPI()
app.add_middleware(SessionMiddleware,
                   secret_key="some-random-string", max_age=None)


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
def signout(request: Request, user_id=int, db: Session = Depends(get_db)):
    print('signout ', user_id)
    user = db.query(models.User).get(user_id)
    print('signout ', user.id)
    user.last_login = datetime.now()
    db.commit()
    db.close()
    url = app.url_path_for("login")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)
# endregion

# region HOME DASHBOARD


@app.post("/home")
def auth(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    d_username = db.query(models.User).filter(
        models.User.username == username).first()
    db.close()
    request.session["my_id"] = d_username.id
    request.session["my_name"] = d_username.name
    request.session["my_username"] = d_username.username
    request.session["my_role"] = d_username.role
    if d_username:
        print('USERNAME FOUND')

        if d_username.password == password:
            context = {"request": request,
                       "greetings": "Hello, " + d_username.name,
                       "last_login": "Your last session was on " + d_username.last_login.strftime("%A %b. %d, %Y at %I:%M %p "),
                       "name": d_username.name,
                       "username": d_username.username,
                       "user_id": d_username.id,
                       "role": d_username.role}
            return templates.TemplateResponse("backend/index.html", context)

        else:
            print('Wrong Password')
            return templates.TemplateResponse("backend/login.html", {"request": request, "error": "Invalid Username/Password"})
    else:
        print("USERNAME NOT FOUND")
        return templates.TemplateResponse("backend/login.html", {"request": request, "error": "Invalid Username/Password"})


# endregion

# region PRODUCTS


@app.get("/list_products")
def list_products(request: Request, db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    
    return templates.TemplateResponse("backend/page-list-product.html", {"request": request,"product_list":products})

@app.get("/add_product")
async def add_product(request: Request, db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    brands=db.query(models.Brand).all()
    warehouses=db.query(models.Warehouse).all()
    db.close()
    context= {"request": request,"category_list":categories,"brand_list":brands,"warehouse_list":warehouses}
    return templates.TemplateResponse("backend/page-add-product.html",context)

@app.post("/create_product")
def create_product(request: Request,
                    product_name: str = Form(...),
                    barcode: str = Form(...),
                    warehouse: str = Form(...),
                    category: str = Form(...),
                    brand: str = Form(...),
                    size: str = Form(...),
                    unit: str = Form(...),
                    cost: str = Form(...),
                    price_standard: str = Form(...),
                    stock_in: str = Form(...),
                    stock_alert: str = Form(...),
                    caption: str = Form(...),
                    description: str = Form(...),
                    db: Session = Depends(get_db)):

    item_name=brand+" "+product_name+" "+size
    ct=datetime.now()
    ts=str(ct.timestamp())[0:10]
    item_code=brand[0:3]+ts
    if len(item_name)>255:
        item_name=item_name[0:255]
    item_name=item_name.upper()

    created_by = request.session.get("my_name", None)
    print('created_by', created_by)
    new_product = models.Product(product_name=product_name,
                                barcode=barcode,
                                warehouse=warehouse,
                                category=category,
                                brand=brand,
                                size=size,
                                unit=unit,
                                cost=cost,
                                price_standard=price_standard,
                                stock_in=stock_in,
                                stock_alert=stock_alert,
                                caption=caption,
                                description=description,
                                item_name=item_name,
                                item_code=item_code,
                                created_by=created_by)
    db.add(new_product)
    db.commit()
    db.close()
    url = app.url_path_for("list_products")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

@app.get("/find_barcode/{barcode}")
async def find_barcode(barcode: str, request: Request, db: Session = Depends(get_db)):
    barcode = db.query(models.Product).filter(
        models.Product.barcode == barcode).first()
    msg = ""
    if not barcode:
        msg = "notfound"
    else:
        msg = "exists"
    return msg

@app.get("/delete_product/{product_id}")
def delete_product(request: Request, product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(
        models.Product.id == product_id).first()
    db.delete(product)
    db.commit()
    db.close()
    url = app.url_path_for("list_products")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)

@app.post("/update_product/{product_id}")
def update_product(request: Request, product_id: int,
                    product_name: str = Form(...),
                    barcode: str = Form(...),
                    warehouse: str = Form(...),
                    category: str = Form(...),
                    brand: str = Form(...),
                    size: str = Form(...),
                    unit: str = Form(...),
                    cost: str = Form(...),
                    price_standard: str = Form(...),
                    stock_in: str = Form(...),
                    stock_alert: str = Form(...),
                    caption: str = Form(...),
                    description: str = Form(...),
                    db: Session = Depends(get_db)):
    print('product_id', product_id)
    d_product = db.query(models.Product).get(product_id)
    print('d_product', d_product)
    created_by = request.session.get("my_name", None)
    if d_product:
        d_product.product_name=product_name
        d_product.barcode=barcode
        d_product.warehouse=warehouse
        d_product.category=category
        d_product.brand=brand
        d_product.size=size
        d_product.unit=unit
        d_product.cost=cost
        d_product.price_standard=price_standard
        d_product.stock_in=stock_in
        d_product.stock_alert=stock_alert
        d_product.caption=caption
        d_product.description=description       
        d_product.update_time = datetime.now()
        d_product.updated_by = created_by
        db.commit()

    db.close()
    url = app.url_path_for("list_products")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@app.get("/get_product/{product_id}")
async def get_product(product_id: int, request: Request, db: Session = Depends(get_db)):
    product = db.query(models.Product).get(product_id)
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    productid = product.id
    print("productid", productid)
    categories = db.query(models.Category).all()
    brands=db.query(models.Brand).all()
    warehouses=db.query(models.Warehouse).all()

   
    context = {"request": request, "productid": productid,
                "product_name": product.product_name.replace(" ","_"),
                "barcode": product.barcode,
                "warehouse": product.warehouse,
                "category": product.category,
                "brand": product.brand,
                "size": product.size,
                "unit": product.unit,
                "cost": product.cost,
                "price_standard": product.price_standard,
                "stock_in": product.stock_in,
                "stock_alert": product.stock_alert,
                "caption": product.caption.replace(" ","_"),
                "description": product.description.replace(" ","_"),
                "category_list":categories,"brand_list":brands,"warehouse_list":warehouses,
                "name": my_name, "username": my_username, "user_id": my_id, "role": my_role}
  
    return templates.TemplateResponse("backend/page-edit-product.html", context)

# endregion

# region CATEGORIES


@app.get("/list_categories")
def list_categories(request: Request, db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    context = {"request": request, "category_list": categories, "name": my_name,
               "username": my_username, "user_id": my_id, "role": my_role}

    return templates.TemplateResponse("backend/page-list-category.html", context)


@app.get("/add_category")
def add_product(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("backend/page-add-category.html", {"request": request})


@app.get("/find_category/{category}")
async def find_category(category: str, request: Request, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(
        models.Category.category == category).first()
    msg = ""
    if not category:
        msg = "notfound"
    else:
        msg = "exists"
    return msg


@app.post("/create_category")
def create_category(request: Request, category: str = Form(...), db: Session = Depends(get_db)):
    print('category', category)
    created_by = request.session.get("my_name", None)
    print('created_by', created_by)
    new_category = models.Category(category=category, created_by=created_by)
    db.add(new_category)
    db.commit()
    db.close()
    url = app.url_path_for("list_categories")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


@app.get("/delete_category/{category_id}")
def delete_user(request: Request, category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(
        models.Category.id == category_id).first()
    db.delete(category)
    db.commit()
    db.close()
    url = app.url_path_for("list_categories")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@app.post("/update_category/{category_id}")
def update_category(request: Request, category_id: int, category: str = Form(...), db: Session = Depends(get_db)):
    print('category_id', category_id)
    d_category = db.query(models.Category).get(category_id)
    print('category', category)
    created_by = request.session.get("my_name", None)
    if category:
        d_category.category = category
        d_category.create_time = datetime.now()
        d_category.created_by = created_by
        db.commit()

    db.close()
    url = app.url_path_for("list_categories")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@app.get("/get_category/{category_id}")
def get_category(category_id: int, request: Request, db: Session = Depends(get_db)):
    category = db.query(models.Category).get(category_id)
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    categorid = category.id
    print("categorid", categorid)
    context = {"request": request, "categorid": categorid, "category": category.category,
               "name": my_name, "username": my_username, "user_id": my_id, "role": my_role}
    return templates.TemplateResponse("backend/page-edit-category.html", context)
# endregion

# region BRANDS
@app.get("/list_brands")
def list_brands(request: Request, db: Session = Depends(get_db)):
    brands = db.query(models.Brand).all()
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    context = {"request": request, "brand_list": brands, "name": my_name,
               "username": my_username, "user_id": my_id, "role": my_role}

    return templates.TemplateResponse("backend/page-list-brand.html", context)


@app.get("/add_brand")
def add_product(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("backend/page-add-brand.html", {"request": request})

@app.get("/find_brand/{brand}")
async def find_brand(brand: str, request: Request, db: Session = Depends(get_db)):
    brand = db.query(models.Brand).filter(
        models.Brand.brand == brand).first()
    msg = ""
    if not brand:
        msg = "notfound"
    else:
        msg = "exists"
    return msg


@app.post("/create_brand")
def create_brand(request: Request, brand: str = Form(...), db: Session = Depends(get_db)):
    print('brand', brand)
    created_by = request.session.get("my_name", None)
    print('created_by', created_by)
    new_brand = models.Brand(brand=brand, created_by=created_by)
    db.add(new_brand)
    db.commit()
    db.close()
    url = app.url_path_for("list_brands")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

@app.get("/delete_brand/{brand_id}")
def delete_brand(request: Request, brand_id: int, db: Session = Depends(get_db)):
    brand = db.query(models.Brand).filter(
        models.Brand.id == brand_id).first()
    db.delete(brand)
    db.commit()
    db.close()
    url = app.url_path_for("list_brands")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)

@app.post("/update_brand/{brand_id}")
def update_brand(request: Request, brand_id: int, brand: str = Form(...), db: Session = Depends(get_db)):
    print('brand_id', brand_id)
    d_brand = db.query(models.Brand).get(brand_id)
    print('brand', d_brand)
    created_by = request.session.get("my_name", None)
    if d_brand:
        d_brand.brand = brand
        d_brand.create_time = datetime.now()
        d_brand.created_by = created_by
        db.commit()

    db.close()
    url = app.url_path_for("list_brands")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@app.get("/get_brand/{brand_id}")
def get_category(brand_id: int, request: Request, db: Session = Depends(get_db)):
    brand = db.query(models.Brand).get(brand_id)
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    brandid = brand.id
    print("brandid", brandid)
    context = {"request": request, "brandid": brandid, "brand": brand.brand,
               "name": my_name, "username": my_username, "user_id": my_id, "role": my_role}
    return templates.TemplateResponse("backend/page-edit-brand.html", context)

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
async def find_username(username: str, request: Request, db: Session = Depends(get_db)):
    username = db.query(models.User).filter(
        models.User.username == username).first()
    msg = ""
    if not username:
        msg = "notfound"
    else:
        msg = "exists"
    return msg


@app.get("/find_staffcode/{staff_code}")
async def find_staffcode(staff_code: str, request: Request, db: Session = Depends(get_db)):
    staff_code = db.query(models.User).filter(
        models.User.staff_code == staff_code).first()
    msg = ""
    if not staff_code:
        msg = "notfound"
    else:
        msg = "exists"
    return msg


@app.get("/get_user/{user_id}")
def get_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    return templates.TemplateResponse("backend/page-edit-user.html", {"request": request, "userid": user.id, "name": user.name, "staff_code": user.staff_code, "username": user.username, "password": user.password, "role": user.role})


@app.post("/create_user")
def create_user(request: Request, name: str = Form(...), staff_code: str = Form(...), username: str = Form(...), password: str = Form(...), role: str = Form(...), db: Session = Depends(get_db)):
    new_user = models.User(name=name, staff_code=staff_code,
                           username=username, password=password, role=role)
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
def update_user(request: Request, user_id: int, name: str = Form(...), staff_code: str = Form(...), username: str = Form(...), password: str = Form(...), role: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    print('user', user.name)

    if user:
        user.name = name
        user.staff_code = staff_code
        user.usernamae = username
        user.password = password
        user.role = role
        db.commit()

    db.close()
    url = app.url_path_for("list_users")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


# endregion
