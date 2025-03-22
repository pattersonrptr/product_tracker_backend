from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from typing import List

from app.schemas.product_schema import ProductCreate, ProductResponse
from app.use_cases.create_product import CreateProduct
from app.use_cases.get_products import GetProducts
from app.use_cases.get_product_by_id import GetProductById
from app.use_cases.get_old_product_urls import GetOldProductUrls
from app.use_cases.update_product import UpdateProduct
from app.use_cases.update_product_by_url import UpdateProductByUrl
from app.use_cases.delete_product import DeleteProduct
from app.services.product_service import ProductService
from app.repositories.product_repository import ProductRepository
from app.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_product_service(db: Session = Depends(get_db)):
    repository = ProductRepository(db)
    return ProductService(repository)

@router.post("/products/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductCreate, product_service: ProductService = Depends(get_product_service)):
    return CreateProduct(product_service).execute(product_data.model_dump())

@router.get("/products/", response_model=List[ProductResponse])
def get_products(url: str = None, product_service: ProductService = Depends(get_product_service)):
    return GetProducts(product_service).execute(url)

@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, product_service: ProductService = Depends(get_product_service)):
    product = GetProductById(product_service).execute(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/products/urls/old/", response_model=List[ProductResponse])
def get_old_product_urls(days: int = 30, product_service: ProductService = Depends(get_product_service)):
    return GetOldProductUrls(product_service).execute(days)

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_data: ProductCreate, product_service: ProductService = Depends(get_product_service)):
    updated_product = UpdateProduct(product_service).execute(product_id, product_data.model_dump())
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@router.put("/products/url/{url:path}", response_model=ProductResponse)
def update_product_by_url(url: str, product_data: ProductCreate, product_service: ProductService = Depends(get_product_service)):
    updated_product = UpdateProductByUrl(product_service).execute(url, product_data.model_dump())
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, product_service: ProductService = Depends(get_product_service)):
    deleted = DeleteProduct(product_service).execute(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")