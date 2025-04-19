from typing import List

from sqlalchemy.orm import Session

from app.entities.product.price_history import PriceHistory
from app.interfaces.repositories.price_history_repository import (
    PriceHistoryRepositoryInterface,
)


class PriceHistoryRepository(PriceHistoryRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def create(self, price_history: PriceHistory) -> PriceHistory:
        try:
            self.db.add(price_history)
            self.db.commit()
            self.db.refresh(price_history)
            return price_history
        except Exception as e:
            self.db.rollback()
            raise e

    def get_by_product_id(self, product_id: int) -> List[PriceHistory]:
        return (
            self.db.query(PriceHistory)
            .filter(PriceHistory.product_id == product_id)
            .all()
        )
