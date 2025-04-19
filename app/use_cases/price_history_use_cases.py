from typing import List

from app.entities.product.price_history import PriceHistory
from app.interfaces.repositories.price_history_repository import (
    PriceHistoryRepositoryInterface,
)


class CreatePriceHistoryUseCase:
    def __init__(self, price_history_repository: PriceHistoryRepositoryInterface):
        self.price_history_repository = price_history_repository

    def execute(self, price_history: PriceHistory) -> PriceHistory:
        return self.price_history_repository.create(price_history)


class GetPriceHistoryByProductIdUseCase:
    def __init__(self, price_history_repository: PriceHistoryRepositoryInterface):
        self.price_history_repository = price_history_repository

    def execute(self, product_id: int) -> List[PriceHistory]:
        return self.price_history_repository.get_by_product_id(product_id)
