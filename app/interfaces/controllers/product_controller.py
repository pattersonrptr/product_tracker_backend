from datetime import datetime
from typing import List
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.infrastructure.database_config import get_db
from app.infrastructure.repositories.product_repository import ProductRepository
from app.infrastructure.repositories.price_history_repository import (
    PriceHistoryRepository,
)
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


router = APIRouter(prefix="/products", tags=["products"])


def get_product_repository(db: Session = Depends(get_db)):
    return ProductRepository(db)


def get_price_history_repository(db: Session = Depends(get_db)):
    return PriceHistoryRepository(db)


@router.post("/", response_model=ProductRead, status_code=201)
def create_product(
    product_in: ProductCreate,
    product_repo: ProductRepository = Depends(get_product_repository),
    price_history_repo: PriceHistoryRepository = Depends(get_price_history_repository),
):
    product_entity = Product(**product_in.model_dump(exclude={"price"}))
    use_case = CreateProductUseCase(product_repo, price_history_repo)
    created_product = use_case.execute(product_entity, product_in.price)
    return created_product


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
    product_in: ProductUpdate,
    product_repo: ProductRepository = Depends(get_product_repository),
    price_history_repo: PriceHistoryRepository = Depends(get_price_history_repository),
):
    use_case = UpdateProductUseCase(product_repo, price_history_repo)
    updated_product = use_case.execute(
        product_id, product_in, product_in.price
    )  # Passando product_in
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
    url: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    created_after: Optional[datetime] = Query(None),
    created_before: Optional[datetime] = Query(None),
    updated_after: Optional[datetime] = Query(None),
    updated_before: Optional[datetime] = Query(None),
    product_repo: ProductRepository = Depends(get_product_repository),
):
    filter_params = {
        "url": url,
        "title": title,
        "min_price": min_price,
        "max_price": max_price,
        "created_after": created_after,
        "created_before": created_before,
        "updated_after": updated_after,
        "updated_before": updated_before,
    }
    use_case = FilterProductsUseCase(product_repo)
    return use_case.execute(filter_params)


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
