from fastapi import FastAPI,Body,Path,Query,Request,HTTPException,Depends
from fastapi.responses import JSONResponse 
from pydantic import BaseModel, Field
from typing import List, Optional
from db.database import Sessionlocal,Base,engine
from models.modelspets import Products as ProductsModel
from models.modelspets import Prices as PricesModel
from pydantic import BaseModel, Field
from fastapi import APIRouter


class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    marca: Optional[str] = None
    
    
routerpets = APIRouter()


@routerpets.post("/petsproduct/", description="Register a new product 1 a 1", tags=["pets"])
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
        
@routerpets.post("/petsbulkupdate/", description="Register a new product in bulk", tags=["pets"])
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