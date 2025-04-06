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


def json_api_response(data, meta=None):
    response = {"data": data}
    if meta:
        response["meta"] = meta
    return response


@router.get("/products/")
def filter_products(
    filter: ProductFilter = Depends(),
    product_service: ProductService = Depends(get_product_service),
):
    filter_use_case = FilterProducts(product_service)
    products = filter_use_case.execute(filter.model_dump(exclude_none=True))
    return json_api_response([product for product in products])


@router.get("/products/{product_id}")
def get_product(
    product_id: int, product_service: ProductService = Depends(get_product_service)
):
    product = GetProductById(product_service).execute(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    print("product: ", product, type(product))
    return json_api_response(product)


@router.get("/products/search/")
def search_products(
    search: ProductSearch = Depends(),
    product_service: ProductService = Depends(get_product_service),
):
    search_use_case = SearchProducts(product_service)
    products = search_use_case.execute(search.query)
    return json_api_response([product for product in products])


@router.get("/products/stats/")
def get_product_stats(product_service: ProductService = Depends(get_product_service)):
    stats_use_case = GetProductStats(product_service)
    stats = stats_use_case.execute()
    return json_api_response(stats)


@router.get("/products/minimal/")
def get_minimal_products(
    product_service: ProductService = Depends(get_product_service),
):
    minimal_use_case = GetMinimalProducts(product_service)
    products = minimal_use_case.execute()
    return json_api_response([product for product in products])


@router.post("/products/", status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    product_service: ProductService = Depends(get_product_service),
):
    product = CreateProduct(product_service).execute(product_data.model_dump())
    print("product: ", product, type(product))
    return json_api_response(product)


@router.post("/products/bulk/", status_code=status.HTTP_201_CREATED)
def bulk_create_products(
    bulk_data: ProductBulkCreate,
    product_service: ProductService = Depends(get_product_service),
):
    products = []
    for product_data in bulk_data.data:
        created_product = CreateProduct(product_service).execute(
            product_data.model_dump()
        )
        products.append(created_product)
    return json_api_response(products)


@router.put("/products/{product_id}")
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
    return json_api_response(updated_product)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int, product_service: ProductService = Depends(get_product_service)
):
    deleted = DeleteProduct(product_service).execute(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return json_api_response(None)
