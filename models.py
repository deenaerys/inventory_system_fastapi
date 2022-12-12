from sqlalchemy import BIGINT, Boolean, Column, Integer, String, DateTime, Float, Text
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

# region WAREHOUSE


class Warehouse(Base):

    __tablename__ = "tblwarehouse"
    id = Column(BIGINT, primary_key=True, index=True,
                autoincrement=True, nullable=False)
    warehouse = Column(String(255))
 # endregion

# region ORDER
class Order(Base):
    __tablename__ = "tblorders"
    id = Column(BIGINT, primary_key=True, index=True,
                autoincrement=True, nullable=False)
    order_id = Column(String(255))
    item_barcode = Column(String(255))
    item_name = Column(String(255))
    item_code = Column(String(255))
    quantity = Column(Float, default=1)
    buyer_name = Column(String(255))
    buyer_address = Column(Text)
    total_amount = Column(Float, default=0)
    fee = Column(Float, default=0)
    charge = Column(Float, default=0)
    sale_invoice = Column(String(255))
    remarks = Column(Text)
    create_time = Column(DateTime, default=datetime.now())
    created_by = Column(String(255))
# endregion

# region PRODUCT


class Product(Base):
    __tablename__ = "tblproducts"
    id = Column(BIGINT, primary_key=True, index=True,
                autoincrement=True, nullable=False)
    barcode = Column(String(255))
    brand = Column(String(255))
    caption = Column(String(255))
    product_name = Column(String(255))
    description = Column(String(255))
    size = Column(String(255))
    unit = Column(String(255))
    category = Column(String(255))
    supplier = Column(String(255))
    cost = Column(Float, default=0)
    price_standard = Column(Float, default=0)
    price_discounted = Column(Float, default=0)
    price_dealer = Column(Float, default=0)
    price_customer = Column(Float, default=0)
    price_notax = Column(Float, default=0)
    price_special = Column(Float, default=0)
    stock_in = Column(BIGINT)
    stock_out = Column(BIGINT)
    stock_alert = Column(Integer)
    item_code = Column(String(255))
    item_name = Column(String(255))
    image = Column(String(255))
    warehouse = Column(String(255))
    remarks = Column(String(255))
    create_time = Column(DateTime, default=datetime.now())
    created_by = Column(String(255))
    update_time = Column(DateTime, default=datetime.now())
    updated_by = Column(String(255))
# endregion

# region OLDCODE


class Todo(Base):
    __tablename__ = "todos"

    id = Column(BIGINT, primary_key=True, index=True)
    title = Column(String(255))
    complete = Column(Boolean, default=False)
# endregion
