from fastapi import FastAPI,Body,Path,Query,Request,HTTPException,Depends
from fastapi.responses import JSONResponse 
from pydantic import BaseModel, Field
from typing import List, Optional
from db.database import Sessionlocal,Base,engine
from models.modelspets import Products as ProductsModel
from models.modelspets import Prices as PricesModel
from pydantic import BaseModel, Field
from fastapi import APIRouter
from sqlalchemy.orm import Session


class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    marca: Optional[str] = None
    
class PriceUpdate(BaseModel):
    sku: str
    tienda: str
    price: Optional[int] = None
    stock: Optional[int] = None
routerpets = APIRouter()

class PriceSchema(BaseModel):
    tienda: str
    price: Optional[int] = None
    stock: Optional[int] = None

    class Config:
        orm_mode = True


class ProductWithPricesSchema(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    marca: Optional[str] = None
    prices: List[PriceSchema]

    class Config:
        orm_mode = True

@routerpets.get("/product/{sku}",tags=["Renderizado"], response_model=ProductWithPricesSchema)
def get_product_with_prices(sku: str):
    db=Sessionlocal
    # Buscar el producto por SKU
    product = db.query(ProductsModel).filter(ProductsModel.sku == sku).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Buscar los precios asociados a ese SKU
    prices = db.query(PricesModel).filter(PricesModel.sku == sku).all()

    # Convertir los resultados de precios a PriceSchema
    price_schemas = [PriceSchema(tienda=price.tienda, price=price.price, stock=price.stock) for price in prices]

    # Construir la respuesta usando los esquemas definidos
    return ProductWithPricesSchema(
        sku=product.sku,
        name=product.name,
        description=product.description,
        category=product.category,
        marca=product.marca,
        prices=price_schemas
    )

@routerpets.post("/petsprice/", description="Register a new price 1 a 1", tags=["pets prices"])
def register_price(price: PriceUpdate):
    db = Sessionlocal()
    try:
        new_price = PricesModel(**price.dict())
        db.add(new_price)
        db.commit()
        db.refresh(new_price)
        return JSONResponse(status_code=201, content={"message": "Price created", "price": new_price.id})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@routerpets.post("/petsbulkprice/", description="Register a new price in bulk", tags=["pets prices"])
def register_prices(prices: List[PriceUpdate]):
    db = Sessionlocal()
    try:
        new_prices = [PricesModel(**price.dict()) for price in prices]
        db.add_all(new_prices)
        db.commit()
        for price in new_prices:
            db.refresh(price)
        return JSONResponse(status_code=201, content={"message": "Prices created", "prices": [price.id for price in new_prices]})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()
        
@routerpets.post("/petsproduct/", description="Register a new product 1 a 1", tags=["pets products"])
def register_product(product: ProductCreate):
    db = Sessionlocal()
    try:
        new_product = ProductsModel(**product.dict())
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return JSONResponse(status_code=201, content={"message": "Product created", "product": new_product.id})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()
        
@routerpets.post("/petsbulkupdate/", description="Register a new product in bulk", tags=["pets products"])
def register_products(products: List[ProductCreate]):
    db = Sessionlocal()
    try:
        new_products = [ProductsModel(**product.dict()) for product in products]
        db.add_all(new_products)
        db.commit()
        for product in new_products:
            db.refresh(product)
        return JSONResponse(status_code=201, content={"message": "Products created", "products": [product.id for product in new_products]})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

