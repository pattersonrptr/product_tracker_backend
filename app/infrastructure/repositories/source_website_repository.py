from typing import Optional, List

from sqlalchemy.orm import Session

from app.entities.product.source_website import SourceWebsite
from app.interfaces.repositories.source_website_repository import (
    SourceWebsiteRepositoryInterface,
)


class SourceWebsiteRepository(SourceWebsiteRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def create(self, source_website: SourceWebsite) -> SourceWebsite:
        try:
            self.db.add(source_website)
            self.db.commit()
            self.db.refresh(source_website)
            return source_website
        except Exception as e:
            self.db.rollback()
            raise e

    def get_by_id(self, source_website_id: int) -> Optional[SourceWebsite]:
        return (
            self.db.query(SourceWebsite)
            .filter(SourceWebsite.id == source_website_id)
            .first()
        )

    def get_by_name(self, name: str) -> Optional[SourceWebsite]:
        return self.db.query(SourceWebsite).filter(SourceWebsite.name == name).first()

    def get_all(self) -> List[SourceWebsite]:
        return self.db.query(SourceWebsite).all()

    def update(
        self, source_website_id: int, source_website: SourceWebsite
    ) -> Optional[SourceWebsite]:
        db_source_website = self.get_by_id(source_website_id)
        if not db_source_website:
            return None
        try:
            for key, value in source_website.__dict__.items():
                if key != "id":
                    setattr(db_source_website, key, value)
            self.db.commit()
            self.db.refresh(db_source_website)
            return db_source_website
        except Exception as e:
            self.db.rollback()
            raise e

    def delete(self, source_website_id: int) -> bool:
        db_source_website = self.get_by_id(source_website_id)
        if not db_source_website:
            return False
        try:
            self.db.delete(db_source_website)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
