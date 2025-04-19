from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.repositories.product_repository import ProductRepository
from app.use_cases.product_use_cases import (
    CreateProductUseCase,
    GetProductByIdUseCase,
    GetProductByUrlUseCase,
    ListProductsUseCase,
    UpdateProductUseCase,
    DeleteProductUseCase,
    SearchProductsUseCase,
    FilterProductsUseCase,
    GetProductStatsUseCase,
    GetMinimalProductsUseCase,
)
from app.entities.product import Product
from app.interfaces.schemas.product_schema import (
    ProductCreate,
    ProductRead,
    ProductUpdate,
    ProductMinimal,
)
from app.interfaces.schemas.product_filter import ProductFilter  # Importe o novo schema

router = APIRouter(prefix="/products", tags=["products"])


def get_product_repository(db: Session = Depends(get_db)):
    return ProductRepository(db)


@router.post("/", response_model=ProductRead, status_code=201)
def create_product(
    product: ProductCreate,
    product_repo: ProductRepository = Depends(get_product_repository),
):
    product_entity = Product(**product.dict())
    use_case = CreateProductUseCase(product_repo)
    return use_case.execute(product_entity)


@router.get("/{product_id}", response_model=ProductRead)
def read_product(
    product_id: int, product_repo: ProductRepository = Depends(get_product_repository)
):
    use_case = GetProductByIdUseCase(product_repo)
    product = use_case.execute(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/url/{url:path}", response_model=ProductRead)
def read_product_by_url(
    url: str, product_repo: ProductRepository = Depends(get_product_repository)
):
    use_case = GetProductByUrlUseCase(product_repo)
    product = use_case.execute(url)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/", response_model=List[ProductRead])
def list_products(product_repo: ProductRepository = Depends(get_product_repository)):
    use_case = ListProductsUseCase(product_repo)
    return use_case.execute()


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    product: ProductUpdate,
    product_repo: ProductRepository = Depends(get_product_repository),
):
    product_entity = Product(**product.dict(exclude_unset=True))
    use_case = UpdateProductUseCase(product_repo)
    updated_product = use_case.execute(product_id, product_entity)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int, product_repo: ProductRepository = Depends(get_product_repository)
):
    use_case = DeleteProductUseCase(product_repo)
    if not use_case.execute(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return {"detail": "Product deleted successfully"}


@router.get("/search/{query}", response_model=List[ProductRead])
def search_products(
    query: str, product_repo: ProductRepository = Depends(get_product_repository)
):
    use_case = SearchProductsUseCase(product_repo)
    return use_case.execute(query)


@router.get("/filter/", response_model=List[ProductRead])
def filter_products(
    filters: ProductFilter = Depends(),
    product_repo: ProductRepository = Depends(get_product_repository),
):
    use_case = FilterProductsUseCase(product_repo)
    return use_case.execute(filters.dict(exclude_unset=True))


@router.get("/stats/", response_model=dict)
def get_product_stats(
    product_repo: ProductRepository = Depends(get_product_repository),
):
    use_case = GetProductStatsUseCase(product_repo)
    return use_case.execute()


@router.get("/minimal/", response_model=List[ProductMinimal])
def get_minimal_products(
    product_repo: ProductRepository = Depends(get_product_repository),
):
    use_case = GetMinimalProductsUseCase(product_repo)
    return use_case.execute()
