from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from typing import List

from app.schemas.product_schema import ProductCreate, ProductResponse
from app.use_cases.create_product import CreateProduct
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
async def create_product(product_data: ProductCreate, product_service: ProductService = Depends(get_product_service)):
    return await CreateProduct(product_service).execute(product_data.model_dump())


@router.get("/products/", response_model=List[ProductResponse])
async def get_products(product_service: ProductService = Depends(get_product_service)):
    return await product_service.get_all_products()


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, product_service: ProductService = Depends(get_product_service)):
    product = await product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product_data: ProductCreate, product_service: ProductService = Depends(get_product_service)):
    updated_product = await product_service.update_product(product_id, product_data.model_dump())
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, product_service: ProductService = Depends(get_product_service)):
    deleted = await product_service.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
