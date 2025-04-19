from abc import ABC, abstractmethod
from typing import List

from app.entities.product.price_history import PriceHistory


class PriceHistoryRepositoryInterface(ABC):
    @abstractmethod
    def create(self, price_history: PriceHistory) -> PriceHistory:
        raise NotImplementedError

    @abstractmethod
    def get_by_product_id(self, product_id: int) -> List[PriceHistory]:
        raise NotImplementedError
