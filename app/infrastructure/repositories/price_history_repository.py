from typing import List, Optional

from sqlalchemy.orm import Session

from app.infrastructure.database.models.price_history_model import (
    PriceHistory as PriceHistoryModel,
)
from app.entities.product import price_history as PriceHistoryEntity
from app.interfaces.repositories.price_history_repository import (
    PriceHistoryRepositoryInterface,
)


class PriceHistoryRepository(PriceHistoryRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def create(
        self, price_history: PriceHistoryEntity.PriceHistory
    ) -> PriceHistoryEntity.PriceHistory:
        try:
            db_price_history = PriceHistoryModel(**price_history.__dict__)
            self.db.add(db_price_history)
            self.db.commit()
            self.db.refresh(db_price_history)
            return PriceHistoryEntity.PriceHistory(**db_price_history.__dict__)
        except Exception as e:
            self.db.rollback()
            raise e

    def get_by_product_id(
        self, product_id: int
    ) -> List[PriceHistoryEntity.PriceHistory]:
        db_price_histories = (
            self.db.query(PriceHistoryModel)
            .filter(PriceHistoryModel.product_id == product_id)
            .all()
        )
        return [
            PriceHistoryEntity.PriceHistory(**db_price_history.__dict__)
            for db_price_history in db_price_histories
        ]

    def get_latest_price(
        self, product_id: int
    ) -> Optional[PriceHistoryEntity.PriceHistory]:
        db_price_history = (
            self.db.query(PriceHistoryModel)
            .filter(PriceHistoryModel.product_id == product_id)
            .order_by(PriceHistoryModel.created_at.desc())
            .first()
        )
        return (
            PriceHistoryEntity.PriceHistory(**db_price_history.__dict__)
            if db_price_history
            else None
        )
