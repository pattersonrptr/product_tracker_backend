from typing import List, Optional
from abc import ABC, abstractmethod

from app.entities import price_history as PriceHistoryEntity


class PriceHistoryRepositoryInterface(ABC):
    @abstractmethod
    def create(
        self, price_history: PriceHistoryEntity.PriceHistory
    ) -> PriceHistoryEntity.PriceHistory:
        raise NotImplementedError

    @abstractmethod
    def get_by_product_id(
        self, product_id: int
    ) -> List[PriceHistoryEntity.PriceHistory]:
        raise NotImplementedError

    @abstractmethod
    def get_latest_price(
        self, product_id: int
    ) -> Optional[PriceHistoryEntity.PriceHistory]:
        raise NotImplementedError
