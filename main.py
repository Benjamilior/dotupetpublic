from fastapi import FastAPI,Body,Path,Query,Request,HTTPException,Depends
from fastapi.responses import JSONResponse 
from pydantic import BaseModel, Field
from typing import List, Optional
from db.database import Sessionlocal,Base,engine
from models.modelspets import Products as ProductsModel
from models.modelspets import Prices as PricesModel
from pydantic import BaseModel, Field
from fastapi import APIRouter
from routers.routerpets import routerpets 
from fastapi.middleware.cors import CORSMiddleware
import os

class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    marca: Optional[str] = None
    links: Optional[str] = None

app = FastAPI(
    title= "API Pets",
    description= "API Pets",
    version= "0.0.1"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(routerpets)

#Creacion de la instacia de Base de Datos
Base.metadata.create_all(bind=engine)


        
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
