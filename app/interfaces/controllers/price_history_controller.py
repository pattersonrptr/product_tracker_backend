from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.repositories.price_history_repository import (
    PriceHistoryRepository,
)
from app.use_cases.price_history_use_cases import (
    CreatePriceHistoryUseCase,
    GetPriceHistoryByProductIdUseCase,
)
from app.entities.product.price_history import PriceHistory
from app.interfaces.schemas.price_history_schema import (
    PriceHistoryCreate,
    PriceHistoryRead,
)

router = APIRouter(prefix="/price_history", tags=["price_history"])


def get_price_history_repository(db: Session = Depends(get_db)):
    return PriceHistoryRepository(db)


@router.post("/", response_model=PriceHistoryRead, status_code=201)
def create_price_history(
    price_history: PriceHistoryCreate,
    price_history_repo: PriceHistoryRepository = Depends(get_price_history_repository),
):
    price_history_entity = PriceHistory(**price_history.dict())
    use_case = CreatePriceHistoryUseCase(price_history_repo)
    return use_case.execute(price_history_entity)


@router.get("/product/{product_id}", response_model=List[PriceHistoryRead])
def get_price_history_by_product(
    product_id: int,
    price_history_repo: PriceHistoryRepository = Depends(get_price_history_repository),
):
    use_case = GetPriceHistoryByProductIdUseCase(price_history_repo)
    history = use_case.execute(product_id)
    return history
