from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.app.infrastructure.database_config import get_db
from src.app.infrastructure.repositories.price_history_repository import (
    PriceHistoryRepository,
)
from src.app.security.auth import get_current_active_user
from src.app.use_cases.price_history_use_cases import (
    CreatePriceHistoryUseCase,
    GetPriceHistoryByProductIdUseCase,
    GetLatestPriceUseCase,
)
from src.app.interfaces.schemas.price_history_schema import (
    PriceHistoryCreate,
    PriceHistoryRead,
)
from src.app.entities.price_history import PriceHistory as PriceHistoryEntity
from src.app.entities.user import User as UserEntity

router = APIRouter(prefix="/price_history", tags=["price_history"])


def get_price_history_repository(db: Session = Depends(get_db)):
    return PriceHistoryRepository(db)


@router.post("/", response_model=PriceHistoryRead, status_code=201)
def create_price_history(
    price_history: PriceHistoryCreate,
    price_history_repo: PriceHistoryRepository = Depends(get_price_history_repository),
    current_user: UserEntity = Depends(get_current_active_user),
):
    price_history_entity = PriceHistoryEntity(**price_history.model_dump())
    use_case = CreatePriceHistoryUseCase(price_history_repo)
    return use_case.execute(price_history_entity)


@router.get("/product/{product_id}", response_model=List[PriceHistoryRead])
def get_price_history_by_product(
    product_id: int,
    price_history_repo: PriceHistoryRepository = Depends(get_price_history_repository),
    current_user: UserEntity = Depends(get_current_active_user),
):
    use_case = GetPriceHistoryByProductIdUseCase(price_history_repo)
    history = use_case.execute(product_id)
    return history


@router.get("/product/{product_id}/latest", response_model=Optional[PriceHistoryRead])
def get_latest_price(
    product_id: int,
    price_history_repo: PriceHistoryRepository = Depends(get_price_history_repository),
):
    use_case = GetLatestPriceUseCase(price_history_repo)
    latest_price = use_case.execute(product_id)
    return latest_price
