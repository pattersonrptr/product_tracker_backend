from typing import Optional, List

from sqlalchemy.orm import Session

from app.infrastructure.database.models.source_website_model import (
    SourceWebsite as SourceWebsiteModel,
)
from app.entities.product import source_website as SourceWebsiteEntity
from app.interfaces.repositories.source_website_repository import (
    SourceWebsiteRepositoryInterface,
)


class SourceWebsiteRepository(SourceWebsiteRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def create(
        self, source_website: SourceWebsiteEntity.SourceWebsite
    ) -> SourceWebsiteEntity.SourceWebsite:
        try:
            db_source_website = SourceWebsiteModel(**source_website.__dict__)
            self.db.add(db_source_website)
            self.db.commit()
            self.db.refresh(db_source_website)
            return SourceWebsiteEntity.SourceWebsite(**db_source_website.__dict__)
        except Exception as e:
            self.db.rollback()
            raise e

    def get_by_id(
        self, source_website_id: int
    ) -> Optional[SourceWebsiteEntity.SourceWebsite]:
        db_source_website = (
            self.db.query(SourceWebsiteModel)
            .filter(SourceWebsiteModel.id == source_website_id)
            .first()
        )
        return (
            SourceWebsiteEntity.SourceWebsite(**db_source_website.__dict__)
            if db_source_website
            else None
        )

    def get_by_name(self, name: str) -> Optional[SourceWebsiteEntity.SourceWebsite]:
        db_source_website = (
            self.db.query(SourceWebsiteModel)
            .filter(SourceWebsiteModel.name == name)
            .first()
        )
        return (
            SourceWebsiteEntity.SourceWebsite(**db_source_website.__dict__)
            if db_source_website
            else None
        )

    def get_all(self) -> List[SourceWebsiteEntity.SourceWebsite]:
        db_source_websites = self.db.query(SourceWebsiteModel).all()
        return [
            SourceWebsiteEntity.SourceWebsite(**db_sw.__dict__)
            for db_sw in db_source_websites
        ]

    def update(
        self, source_website_id: int, source_website: SourceWebsiteEntity.SourceWebsite
    ) -> Optional[SourceWebsiteEntity.SourceWebsite]:
        db_source_website = self.get_by_id(source_website_id)
        if not db_source_website:
            return None
        try:
            for key, value in source_website.__dict__.items():
                if key != "id":
                    setattr(db_source_website, key, value)
            self.db.commit()
            self.db.refresh(db_source_website)
            return SourceWebsiteEntity.SourceWebsite(**db_source_website.__dict__)
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
