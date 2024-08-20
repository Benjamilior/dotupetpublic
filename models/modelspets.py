from db.database import Base
from sqlalchemy import Column, Integer, String


class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sku = Column(String, unique=True, index=True)
    name = Column(String)
    description = Column(String)
    category = Column(String)
    marca = Column(String)

class Prices(Base):
    __tablename__ = 'prices'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sku = Column(String, index=True)
    tienda = Column(String)
    price = Column(Integer)
    stock = Column(Integer)