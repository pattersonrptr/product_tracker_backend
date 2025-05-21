from typing import Optional, List, Tuple, Dict, Any

from sqlalchemy import func, desc, asc
from sqlalchemy.orm import Session

from src.app.infrastructure.database.models.source_website_model import (
    SourceWebsite as SourceWebsiteModel,
)
from src.app.entities import source_website as SourceWebsiteEntity
from src.app.interfaces.repositories.source_website_repository import (
    SourceWebsiteRepositoryInterface,
)


class SourceWebsiteRepository(SourceWebsiteRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def create(
        self, source_website: SourceWebsiteEntity.SourceWebsite
    ) -> SourceWebsiteEntity.SourceWebsite:
        db_source_website = SourceWebsiteModel(**source_website.model_dump())
        self.db.add(db_source_website)
        self.db.commit()
        self.db.refresh(db_source_website)
        return SourceWebsiteEntity.SourceWebsite(**db_source_website.__dict__)

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

    def get_all(
            self,
            limit: int,
            offset: int,
            filter_params: Optional[Dict[str, Any]] = None,
            sort_by: Optional[str] = None,
            sort_order: Optional[str] = None
    ) -> Tuple[List[SourceWebsiteEntity.SourceWebsite], int]:
        query = self.db.query(SourceWebsiteModel)

        if filter_params:
            if filter_params.get("name"):
                query = query.filter(SourceWebsiteModel.name.ilike(f"%{filter_params['name']}%"))
            if filter_params.get("is_active") is not None:
                query = query.filter(SourceWebsiteModel.is_active == filter_params['is_active'])
            if filter_params.get("base_url"):
                query = query.filter(SourceWebsiteModel.base_url.ilike(f"%{filter_params['base_url']}%"))

        total_count = query.count()

        if sort_by:
            sort_column = getattr(SourceWebsiteModel, sort_by, None)
            if sort_column:
                if sort_order == 'desc':
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(asc(sort_column))

        db_source_websites = query.offset(offset).limit(limit).all()

        items = [
            SourceWebsiteEntity.SourceWebsite(**db_sw.__dict__)
            for db_sw in db_source_websites
        ]
        return items, total_count

    def update(
        self, source_website_id: int, source_website: SourceWebsiteEntity.SourceWebsite
    ) -> Optional[SourceWebsiteEntity.SourceWebsite]:
        db_source_website_model = (
            self.db.query(SourceWebsiteModel)
            .filter(SourceWebsiteModel.id == source_website_id)
            .first()
        )
        if not db_source_website_model:
            return None
        try:
            for key, value in source_website.model_dump(exclude_unset=True).items():
                setattr(db_source_website_model, key, value)
            self.db.commit()
            self.db.refresh(db_source_website_model)
            return SourceWebsiteEntity.SourceWebsite(**db_source_website_model.__dict__)
        except Exception as e:
            self.db.rollback()
            raise e

    def delete(self, source_website_id: int) -> bool:
        db_source_website_model = (
            self.db.query(SourceWebsiteModel)
            .filter(SourceWebsiteModel.id == source_website_id)
            .first()
        )
        if not db_source_website_model:
            return False
        try:
            self.db.delete(db_source_website_model)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e
