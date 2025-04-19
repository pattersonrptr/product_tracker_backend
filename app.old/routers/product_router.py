from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repositories.product_repository import ProductRepository
from app.schemas.product_schema import (
    ProductBulkCreate,
    ProductCreate,
    ProductFilter,
    ProductPartialResponse,
    ProductResponse,
    ProductSearch,
    ProductStats,
    ProductUpdate,
)
from app.services.product_service import ProductService
from app.use_cases.product_use_cases import (
    CreateProduct,
    DeleteProduct,
    FilterProducts,
    GetMinimalProducts,
    GetProductById,
    GetProductStats,
    SearchProducts,
    UpdateProduct,
)

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


@router.get("/products/", response_model=List[ProductResponse])
def filter_products(
    filter: ProductFilter = Depends(),
    product_service: ProductService = Depends(get_product_service),
):
    filter_use_case = FilterProducts(product_service)
    return filter_use_case.execute(filter.model_dump(exclude_none=True))


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int, product_service: ProductService = Depends(get_product_service)
):
    product = GetProductById(product_service).execute(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/products/search/", response_model=List[ProductResponse])
def search_products(
    search: ProductSearch = Depends(),
    product_service: ProductService = Depends(get_product_service),
):
    search_use_case = SearchProducts(product_service)
    return search_use_case.execute(search.query)


@router.get("/products/stats/", response_model=ProductStats)
def get_product_stats(product_service: ProductService = Depends(get_product_service)):
    stats_use_case = GetProductStats(product_service)
    return stats_use_case.execute()


@router.get("/products/minimal/", response_model=List[ProductPartialResponse])
def get_minimal_products(
    product_service: ProductService = Depends(get_product_service),
):
    minimal_use_case = GetMinimalProducts(product_service)
    return minimal_use_case.execute()


@router.post(
    "/products/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED
)
def create_product(
    product_data: ProductCreate,
    product_service: ProductService = Depends(get_product_service),
):
    return CreateProduct(product_service).execute(product_data.model_dump())


@router.post(
    "/products/bulk/",
    response_model=List[ProductResponse],
    status_code=status.HTTP_201_CREATED,
)
def bulk_create_products(
    bulk_data: ProductBulkCreate,
    product_service: ProductService = Depends(get_product_service),
):
    return [
        CreateProduct(product_service).execute(product.model_dump())
        for product in bulk_data.products
    ]


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    product_service: ProductService = Depends(get_product_service),
):
    updated_product = UpdateProduct(product_service).execute(
        product_id, product_data.model_dump(exclude_unset=True)
    )
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int, product_service: ProductService = Depends(get_product_service)
):
    deleted = DeleteProduct(product_service).execute(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
