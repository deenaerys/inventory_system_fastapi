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

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Optional
from sqlalchemy import desc

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
@app.get("/dashboard")
def dashboard(request:Request,db:Session=Depends(get_db)):
    products = db.query(models.Product).all()
    suppliers=db.query(models.Supplier).all()
    db.close()
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)
    
    context = {"request": request,
                       "greetings": "Hello, " + my_name,
                       "last_login": "Your last session was on " + my_login,
                       "name": my_name,
                       "username": my_username,
                       "user_id": my_id,
                       "role": my_role,
                       "product_list":products,
                       "supplier_list":suppliers}
    return templates.TemplateResponse("backend/index.html", context)

@app.post("/home")
def auth(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    d_username = db.query(models.User).filter(models.User.username == username).first()
    db.close()
    
    if d_username:
        print('USERNAME FOUND')

        if d_username.password == password:
            request.session["my_id"] = d_username.id
            request.session["my_name"] = d_username.name
            request.session["my_username"] = d_username.username
            request.session["my_role"] = d_username.role
            request.session["my_login"] = str(d_username.last_login.strftime("%A %b. %d, %Y at %I:%M %p "))
            
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

@app.post("/main")
def main(request: Request, code: str = Form(...),db: Session = Depends(get_db)):
    d_username = db.query(models.User).filter(models.User.staff_code == code).first()
    products = db.query(models.Product).all()
    suppliers=db.query(models.Supplier).all()
    db.close()
    
    if d_username:
        print('CODE FOUND')
        request.session["my_id"] = d_username.id
        request.session["my_name"] = d_username.name
        request.session["my_username"] = d_username.username
        request.session["my_role"] = d_username.role
        request.session["my_login"] = str(d_username.last_login.strftime("%A %b. %d, %Y at %I:%M %p "))
        
        context = {"request": request,
                       "greetings": "Hello, " + d_username.name,
                       "last_login": "Your last session was on " + d_username.last_login.strftime("%A %b. %d, %Y at %I:%M %p "),
                       "name": d_username.name,
                       "username": d_username.username,
                       "user_id": d_username.id,
                       "role": d_username.role,
                       "product_list":products,
                       "supplier_list":suppliers}
        return templates.TemplateResponse("backend/index.html", context)
      
    else:
        print("CODE NOT FOUND")
        return templates.TemplateResponse("backend/login.html", {"request": request, "error": "Invalid Code"})




# endregion


# region "ORDER"
@app.get("/order")
def order(request:Request,db:Session=Depends(get_db)):    
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)
    ct=datetime.now()
    ts=str(ct.timestamp())[0:10]
    if len(str(my_id))<2:
        pref='{:0>2}'.format(int(my_id))       
        
    else:
        pref=my_id
       
    order_id=pref+ts
    request.session["my_order"] = order_id
    context = {"request": request,
                       "greetings": "Hello, " + my_name,
                       "last_login": "Your last session was on " + my_login,
                       "name": my_name,
                       "username": my_username,
                       "user_id": my_id,
                       "role": my_role,
                       "order_id":order_id}
    return templates.TemplateResponse("backend/order.html", context)

@app.post("/add_order/{barcode}/{item_name}/{qty}/{price}/{amt}")
async def add_order(request:Request,barcode:str,item_name:str,qty:str,price:str,amt:str,db:Session=Depends(get_db)):   
    my_name = request.session.get("my_name", None)
    my_order = request.session.get("my_order",None)    
    new_order = models.Order(order_id=my_order,
                            item_barcode =barcode,
                            item_name = item_name,    
                            quantity = qty, 
                            price = price,
                            amount = amt,
                            create_time =datetime.now(),
                            created_by = my_name)
    db.add(new_order)
    db.commit()
    db.close()

@app.post("/save_order/{order_id}")
async def save_order(request:Request,
                    order_id:str,                                    
                    total_count:str=Form(...),
                    total_amount:str=Form(...),
                    buyer_name:str= Form(...),
                    buyer_address:str= Form(...),
                    fee:str= Form(...),
                    charge:str= Form(...),
                    sale_invoice:str= Form(...),
                    remarks:str= Form(...),
                    db:Session=Depends(get_db)): 
    my_name = request.session.get("my_name", None)
    print(f'/save_order/','TOTAL AMT',total_amount,'   TOTAL CNT',total_count)           
    new_orderstatus=models.OrderStatus(order_id=order_id,
                                        total_amount=total_amount,
                                        total_count=total_count,
                                        buyer_name=buyer_name,
                                        buyer_address=buyer_address,
                                        fee=fee,
                                        charge=charge,
                                        sale_invoice=sale_invoice,
                                        remarks=remarks,
                                        create_time=datetime.now(),
                                        update_time=datetime.now(),
                                        created_by=my_name,
                                        status="Created",details=my_name)
    db.add(new_orderstatus)
    db.commit()
    less_stock(db,order_id)
    db.close()
    
    url = app.url_path_for("list_orders")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)   
   
    
@app.post("/update_order/{order_id}")
async def update_order(request:Request,
                    order_id:str,
                    order_status:str=Form(...),
                    details:str=Form(...),
                    total_count:str=Form(...),
                    total_amount:str=Form(...),
                    buyer_name:str= Form(...),
                    buyer_address:str= Form(...),
                    fee:str= Form(...),
                    charge:str= Form(...),
                    sale_invoice:str= Form(...),
                    remarks:str= Form(...),
                    db:Session=Depends(get_db)): 
               
    order = db.query(models.OrderStatus).filter(models.OrderStatus.order_id== order_id).first()
    if order:
        order.status=order_status
        order.details=details
        order.update_time=datetime.now()
        order.total_count = total_count
        order.total_amount= total_amount
        order.buyer_name=buyer_name
        order.buyer_address=buyer_address
        order.fee=fee
        order.charge=charge
        order.sale_invoice=sale_invoice
        order.remarks=remarks            
        db.commit()

        if order_status=="Packed":less_stock(db,order_id)
        if order_status=="Cancelled":return_stock(db,order_id)    

    db.close()
    
    url = app.url_path_for("list_orders")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

def less_stock(db,order_id):
    items=db.query(models.Order).filter(models.Order.order_id==order_id).all()
    for item in items:
        barcode=item.item_barcode
        less=item.quantity
        instock=db.query(models.Product).filter(models.Product.barcode==barcode).first()
           
        if instock:
            instock.stock_in-=less
            instock.update_time=datetime.now()
            instock.updated_by=order_id
            db.commit()
    db.close()

def return_stock(db,order_id):
    items=db.query(models.Order).filter(models.Order.order_id==order_id).all()
    for item in items:
        barcode=item.item_barcode
        ret=item.quantity
        instock=db.query(models.Product).filter(models.Product.barcode==barcode).first()
           
        if instock:
            instock.stock_in+=ret
            instock.update_time=datetime.now()
            instock.updated_by=order_id
            db.commit()
    db.close()

@app.get("/list_orders")
def list_orders(request: Request, db: Session = Depends(get_db)):
    orders = db.query(models.OrderStatus).all()
    db.close()
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)
    context={"request": request,
            "greetings": "Hello, " + my_name,
            "last_login": "Your last session was on " + my_login,
            "name": my_name,
            "username": my_username,
            "user_id": my_id,
            "role": my_role,
            "order_list":orders}
    
    return templates.TemplateResponse("backend/page-list-order.html", context)

@app.get('/order_slip/{order_id}')
async def order_slip(request: Request,order_id:str, db: Session = Depends(get_db)):
    my_name = request.session.get("my_name", None)
    order = db.query(models.Order).filter(models.Order.order_id == order_id).all()
    orderstatus=db.query(models.OrderStatus).filter(models.OrderStatus.order_id==order_id).first()
    db.close()


    context={"request":request,
             "my_name":my_name,
             "order_list":order,
             "orderstatus":orderstatus,
             "order_id":order_id}

    return templates.TemplateResponse("backend/order_slip.html",context)

@app.get('/get_order/{order_id}')
async def get_order(request: Request,order_id:str,db:Session=Depends(get_db)):
    orderstatus=db.query(models.OrderStatus).filter(models.OrderStatus.order_id==order_id).first()
    os=orderstatus.status
    db.close()
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)
    context={"request": request,
            "greetings": "Hello, " + my_name,
            "last_login": "Your last session was on " + my_login,
            "name": my_name,
            "username": my_username,
            "user_id": my_id,
            "role": my_role,
            "orderstatus":orderstatus,"os":os}
    return templates.TemplateResponse("backend/page-edit-order.html", context)



@app.get("/search_order")
async def search_order(request:Request,db:Session=Depends(get_db),param: Optional[str] = None):
    orders = db.query(models.OrderStatus).filter(models.OrderStatus.order_id.like(param+"%"))
    db.close()    
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)
    context={"request": request,
            "greetings": "Hello, " + my_name,
            "last_login": "Your last session was on " + my_login,
            "name": my_name,
            "username": my_username,
            "user_id": my_id,
            "role": my_role,
            "order_list":orders}
    
    return templates.TemplateResponse("backend/page-list-order.html", context)

@app.get("/get_productnames")
async def get_productnames(request: Request, db: Session = Depends(get_db)):
    productnames=db.query(models.Product).all()
    db.close()
    namelist=[]
    for n in productnames:
        namelist.append(n.product_name)
    
    result=jsonable_encoder(namelist)
    return JSONResponse(content=result)

@app.get("/delete_order_item/{orderid}/{itemname}/{itembarcode}")
async def delete_order_item(orderid:str,itemname:str,itembarcode:str,request: Request, db: Session = Depends(get_db)):
    orderid=orderid.strip()
    itemname=itemname.strip()
    itembarcode=itembarcode.strip()   
    item=db.query(models.Order).filter(models.Order.order_id==orderid,models.Order.item_name==itemname,models.Order.item_barcode==itembarcode).first()
    if item:
        db.delete(item)
        db.commit()
        db.close()
        return JSONResponse(jsonable_encoder("FOUND"))

@app.post("/update_order_item/{orderid}/{itemname}/{itembarcode}/{itemquantity}")
async def update_order_item(orderid:str,itemname:str,itembarcode:str,itemquantity:str,request: Request, db: Session = Depends(get_db)):
    orderid=orderid.strip()
    itemname=itemname.strip()
    itembarcode=itembarcode.strip()
    itemquantity=itemquantity.strip()
    
    item=db.query(models.Order).filter(models.Order.order_id==orderid,models.Order.item_name==itemname,models.Order.item_barcode==itembarcode).first()
    if item:
        item.quantity=itemquantity
        item.amount=float(itemquantity)*float(item.price)
        db.commit()
        db.close()
        return JSONResponse(jsonable_encoder("FOUND"))  

# endregion

# region PRODUCTS
@app.get("/list_products")
def list_products(request: Request, db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    db.close()
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)
    context={"request": request,
            "greetings": "Hello, " + my_name,
            "last_login": "Your last session was on " + my_login,
            "name": my_name,
            "username": my_username,
            "user_id": my_id,
            "role": my_role,
            "product_list":products}
    
    return templates.TemplateResponse("backend/page-list-product.html", context)

@app.get("/search_product")
async def search_product(request:Request,db:Session=Depends(get_db),param: Optional[str] = None):
    products = db.query(models.Product).filter(models.Product.barcode.like(param+"%"))
    db.close()    
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)
    context={"request": request,
            "greetings": "Hello, " + my_name,
            "last_login": "Your last session was on " + my_login,
            "name": my_name,
            "username": my_username,
            "user_id": my_id,
            "role": my_role,
            "product_list":products}
    
    return templates.TemplateResponse("backend/page-list-product.html", context)

@app.get("/add_product")
async def add_product(request: Request, db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    brands=db.query(models.Brand).all()
    warehouses=db.query(models.Warehouse).all()
    db.close()
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)
    context= {"request": request,
            "greetings": "Hello, " + my_name,
            "last_login": "Your last session was on " + my_login,
            "name": my_name,
            "username": my_username,
            "user_id": my_id,
            "role": my_role,
            "category_list":categories,"brand_list":brands,"warehouse_list":warehouses}
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
    if not caption:
        caption='caption'
    if not description:
        description='description'


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

@app.get("/find_product/{barcode}")
async def find_product(barcode: str, request: Request, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(
        models.Product.barcode == barcode).first()
    db.close()    
    if not product:
        return "NOTFOUND"
        
    else:
        barcode=product.barcode
        item_name=product.item_name
        price_standard="{:.2f}".format(product.price_standard)        
       
        return str(barcode)+"~"+str(item_name)+"~"+str(price_standard)
        
@app.get("/find_productname/{productname}")
async def find_productname(productname:str,request: Request, db: Session = Depends(get_db)):
    print(productname)
    product=db.query(models.Product).filter(models.Product.product_name==productname).first()
    db.close()
    if not product:
        return "NOTFOUND"
    else:
        barcode=product.barcode
        item_name=product.item_name
        price_standard="{:.2f}".format(product.price_standard)
        return str(barcode)+"~"+str(item_name)+"~"+str(price_standard)


@app.get("/find_barcode/{barcode}")
async def find_barcode(barcode: str, request: Request, db: Session = Depends(get_db)):
    barcode = db.query(models.Product).filter(
        models.Product.barcode == barcode).first()
    
    msg = ""
    db.close()
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
    my_login=request.session.get("my_login",None)
    productid = product.id
    print("productid", productid)
    categories = db.query(models.Category).all()
    brands=db.query(models.Brand).all()
    warehouses=db.query(models.Warehouse).all()
    db.close()

   
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
                "last_login": "Your last session was on " + my_login,
                "name": my_name, "username": my_username, "user_id": my_id, "role": my_role}
  
    return templates.TemplateResponse("backend/page-edit-product.html", context)

@app.post("/update_stock")
async def update_stock(request: Request,db: Session = Depends(get_db)):
    req=await request.body()
    req=req.decode("utf-8").replace(",",":").replace('"',"").replace("{","").replace("}","").split(":")       
    barcode=req[1]
    quantity=req[3]
    remarks=req[5]
    item=db.query(models.Product).filter(models.Product.barcode==barcode).first()
    db.close()
    if item:
        item.stock_in+=int(quantity)
        item.remarks=remarks
        db.commit()
        result = jsonable_encoder("OK")
        
    else:
        result= jsonable_encoder("NOT FOUND")

    return JSONResponse(content=result)

def low_stocks():
    with engine.connect() as con:
        rs=con.execute("SELECT * FROM tblproducts WHERE stock_in<=stock_alert")
        con.close()
        return rs

@app.get("/lowstock")
def lowstock(request: Request, db: Session = Depends(get_db)):
    LS=low_stocks()
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)
    context={"request": request,
            "greetings": "Hello, " + my_name,
            "last_login": "Your last session was on " + my_login,
            "name": my_name,
            "username": my_username,
            "user_id": my_id,
            "role": my_role,
            "lowstock":LS}
    
    return templates.TemplateResponse("backend/page-list-lowstock.html", context)

# endregion

# region CATEGORIES
@app.get("/list_categories")
def list_categories(request: Request, db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    db.close()
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)
    context = {"request": request, "category_list": categories, "name": my_name,"last_login": "Your last session was on " + my_login,
               "username": my_username, "user_id": my_id, "role": my_role}

    return templates.TemplateResponse("backend/page-list-category.html", context)


@app.get("/add_category")
def add_product(request: Request, db: Session = Depends(get_db)):
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)
    context = {"request": request, "name": my_name,"last_login": "Your last session was on " + my_login,
               "username": my_username, "user_id": my_id, "role": my_role}
    return templates.TemplateResponse("backend/page-add-category.html", context)


@app.get("/find_category/{category}")
async def find_category(category: str, request: Request, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(
        models.Category.category == category).first()
    db.close()
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
    db.close()
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)
    categorid = category.id
   
    context = {"request": request, "categorid": categorid, "category": category.category,"last_login": "Your last session was on " + my_login,
               "name": my_name, "username": my_username, "user_id": my_id, "role": my_role}
    return templates.TemplateResponse("backend/page-edit-category.html", context)
# endregion

# region BRANDS
@app.get("/list_brands")
def list_brands(request: Request, db: Session = Depends(get_db)):
    brands = db.query(models.Brand).all()
    db.close()
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)
    context = {"request": request, "brand_list": brands, "name": my_name,"last_login": "Your last session was on " + my_login,
               "username": my_username, "user_id": my_id, "role": my_role}

    return templates.TemplateResponse("backend/page-list-brand.html", context)


@app.get("/add_brand")
def add_product(request: Request, db: Session = Depends(get_db)):
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)
    context = {"request": request, "name": my_name,"last_login": "Your last session was on " + my_login,
               "username": my_username, "user_id": my_id, "role": my_role}
    return templates.TemplateResponse("backend/page-add-brand.html", context)

@app.get("/find_brand/{brand}")
async def find_brand(brand: str, request: Request, db: Session = Depends(get_db)):
    brand = db.query(models.Brand).filter(
        models.Brand.brand == brand).first()
    db.close()
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
def get_brand(brand_id: int, request: Request, db: Session = Depends(get_db)):
    brand = db.query(models.Brand).get(brand_id)
    db.close()
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)
    brandid = brand.id
    print("brandid", brandid)
    context = {"request": request, "brandid": brandid, "brand": brand.brand,"last_login": "Your last session was on " + my_login,
               "name": my_name, "username": my_username, "user_id": my_id, "role": my_role}
    return templates.TemplateResponse("backend/page-edit-brand.html", context)

# endregion

# region SALES
@app.get("/list_sales")
def list_sales(request: Request, db: Session = Depends(get_db)):
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)    
    
    context = {"request": request, "last_login": "Your last session was on " + my_login,
               "name": my_name, "username": my_username, "user_id": my_id, "role": my_role}
    return templates.TemplateResponse("backend/page-list-sale.html", context)


@app.get("/add_sale")
def add_product(request: Request, db: Session = Depends(get_db)):
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)    
    
    context = {"request": request, "last_login": "Your last session was on " + my_login,
               "name": my_name, "username": my_username, "user_id": my_id, "role": my_role}
    return templates.TemplateResponse("backend/page-add-sale.html", context)
# endregion

# region PURCHASES
@app.get("/list_puchases")
def list_puchases(request: Request, db: Session = Depends(get_db)):
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)    
    
    context = {"request": request, "last_login": "Your last session was on " + my_login,
               "name": my_name, "username": my_username, "user_id": my_id, "role": my_role}
    return templates.TemplateResponse("backend/page-list-purchase.html", context)


@app.get("/add_purchase")
def add_purchase(request: Request, db: Session = Depends(get_db)):
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)    
    
    context = {"request": request, "last_login": "Your last session was on " + my_login,
               "name": my_name, "username": my_username, "user_id": my_id, "role": my_role}
    return templates.TemplateResponse("backend/page-add-purchase.html", context)

# endregion

# region RETURNS
@app.get("/list_returns")
def list_returns(request: Request, db: Session = Depends(get_db)):
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)    
    
    context = {"request": request, "last_login": "Your last session was on " + my_login,
               "name": my_name, "username": my_username, "user_id": my_id, "role": my_role}
    return templates.TemplateResponse("backend/page-list-returns.html", context)


@app.get("/add_return")
def add_return(request: Request, db: Session = Depends(get_db)):
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)    
    
    context = {"request": request, "last_login": "Your last session was on " + my_login,
               "name": my_name, "username": my_username, "user_id": my_id, "role": my_role}
    return templates.TemplateResponse("backend/page-add-return.html", context)
# endregion

# region USERS
@app.get("/list_users")
def list_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    db.close()
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)    
    
    context = {"request": request,"user_list": users, "last_login": "Your last session was on " + my_login,
               "name": my_name, "username": my_username, "user_id": my_id, "role": my_role}
    return templates.TemplateResponse("backend/page-list-users.html", context)

@app.get("/search_name")
async def search_order(request:Request,db:Session=Depends(get_db),param: Optional[str] = None):
    users = db.query(models.User).filter(models.User.name.like(param+"%"))
    db.close()
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)    
    
    context = {"request": request,"user_list": users, "last_login": "Your last session was on " + my_login,
               "name": my_name, "username": my_username, "user_id": my_id, "role": my_role}
    return templates.TemplateResponse("backend/page-list-users.html", context)

@app.get("/add_user_page")
def add_user_page(request: Request, db: Session = Depends(get_db)):
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)    
    
    context = {"request": request, "last_login": "Your last session was on " + my_login,
               "name": my_name, "username": my_username, "user_id": my_id, "role": my_role}
    return templates.TemplateResponse("backend/page-add-user.html",context)


@app.get("/find_username/{username}")
async def find_username(username: str, request: Request, db: Session = Depends(get_db)):
    username = db.query(models.User).filter(
        models.User.username == username).first()
    msg = ""
    db.close()
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
    db.close()
    if not staff_code:
        msg = "notfound"
    else:
        msg = "exists"
    return msg


@app.get("/get_user/{user_id}")
def get_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = db.query(models.User).get(user_id)
    db.close()
    my_id = request.session.get("my_id", None)
    my_name = request.session.get("my_name", None)
    my_username = request.session.get("my_username", None)
    my_role = request.session.get("my_role", None)
    my_login=request.session.get("my_login",None)    
    
    context = {"request": request, "last_login": "Your last session was on " + my_login,
               "name": my_name, "username": my_username, "user_id": my_id, "role": my_role,
               "userid": user.id, "name": user.name, "staff_code": user.staff_code, "username": user.username, "password": user.password, "role": user.role}
    return templates.TemplateResponse("backend/page-edit-user.html", context)


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
