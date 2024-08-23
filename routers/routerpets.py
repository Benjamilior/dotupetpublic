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
from typing import List, Optional


class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    marca: Optional[str] = None
    links: Optional[str] = None
    
class PriceUpdate(BaseModel):
    sku: str
    tienda: str
    price: Optional[int] = None
    stock: Optional[int] = None
    link: Optional[str] = None

class PriceSchema(BaseModel):
    tienda: str
    price: Optional[int] = None
    stock: Optional[int] = None
    link: Optional[str] = None

    class Config:
        orm_mode = True


class ProductWithPricesSchema(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    marca: Optional[str] = None
    links: Optional[str] = None
    prices: List[PriceSchema]

    class Config:
        orm_mode = True

routerpets = APIRouter()

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()
        
        
#Busqueda de Info por SKU
@routerpets.get("/product/{sku}", description="Get product by SKU", tags=["Renderizado"], response_model=ProductWithPricesSchema)
def get_product_with_prices(sku: str, db: Session = Depends(get_db)):
    # Buscar el producto por SKU
    product = db.query(ProductsModel).filter(ProductsModel.sku == sku).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Buscar los precios asociados a ese SKU
    prices = db.query(PricesModel).filter(PricesModel.sku == sku).all()

    # Convertir los resultados de precios a PriceSchema
    price_schemas = [PriceSchema(tienda=price.tienda, price=price.price, stock=price.stock, link=price.link) for price in prices]

    # Construir la respuesta usando los esquemas definidos
    return ProductWithPricesSchema(
        sku=product.sku,
        name=product.name,
        description=product.description,
        category=product.category,
        marca=product.marca,
        links=product.links,
        prices=price_schemas,
        
    )


      
#Para Subir Info        
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

#Subir productos en masa
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


class LinkUpdate(BaseModel):
    links: str
@routerpets.put("/petsproductput/{sku}", description="Update product links by SKU", tags=["pets products"])
def update_product(sku: str, link_update: LinkUpdate):
    db = Sessionlocal()
    try:
        # Query the product by SKU
        db_product = db.query(ProductsModel).filter(ProductsModel.sku == sku).first()
        
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Update the 'links' field
        db_product.links = link_update.links
        
        # Commit the changes
        db.commit()
        db.refresh(db_product)
        
        return {"message": "Product links updated", "product": db_product.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

class LinkUpdateBulk(BaseModel):
    sku: str
    links: str
@routerpets.put("/bulk_update_products", description="Bulk update product links by SKU", tags=["pets products"])
def bulk_update_products(products: List[LinkUpdateBulk]):
    db = Sessionlocal()
    try:
        updated_products = []
        for product in products:
            # Query the product by SKU
            db_product = db.query(ProductsModel).filter(ProductsModel.sku == product.sku).first()
            
            if not db_product:
                raise HTTPException(status_code=404, detail=f"Product with SKU {product.sku} not found")
            
            # Update the 'links' field
            db_product.links = product.links
            
            updated_products.append(db_product.id)
        
        # Commit the changes
        db.commit()
        
        return {"message": "Product links updated", "updated_products": updated_products}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

class PriceUpdateBulk(BaseModel):
    sku: str
    tienda: str
    price: Optional[int] = None
    stock: Optional[int] = None
    
@routerpets.put("/bulk_update_prices", description="Bulk update price and stock by SKU and store", tags=["pets prices"])
def bulk_update_prices(price_updates: List[PriceUpdateBulk], db: Session = Depends(get_db)):
    try:
        updated_records = []
        for update in price_updates:
            # Buscar el registro de precio por SKU y tienda
            price_record = db.query(PricesModel).filter(PricesModel.sku == update.sku, PricesModel.tienda == update.tienda).first()
            
            if not price_record:
                raise HTTPException(status_code=404, detail=f"Price record with SKU {update.sku} and store {update.tienda} not found")
            
            # Actualizar el precio y stock si se proporcionan nuevos valores
            if update.price is not None:
                price_record.price = update.price
            if update.stock is not None:
                price_record.stock = update.stock
            
            updated_records.append({"sku": update.sku, "tienda": update.tienda})
        
        # Confirmar los cambios
        db.commit()
        
        return {"message": "Prices and stock updated", "updated_records": updated_records}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()
