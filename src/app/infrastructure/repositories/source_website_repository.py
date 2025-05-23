from typing import Optional, List, Tuple, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import or_, inspect
from sqlalchemy.types import Boolean


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
        column_filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> Tuple[List[SourceWebsiteEntity.SourceWebsite], int]:
        query = self.db.query(SourceWebsiteModel)

        if column_filters:
            for field, filter_info in column_filters.items():
                value = filter_info.get("value")
                operator = filter_info.get("operator", "equals")

                column = getattr(SourceWebsiteModel, field, None)
                if column is None:
                    print(f"Warning: Filter field '{field}' not found on SourceWebsiteModel.")
                    continue

                column_type = inspect(column).type if hasattr(inspect(column), 'type') else None


                if value is None:
                    if operator == 'isEmpty':
                        query = query.filter(column.is_(None) | (column == ''))
                    elif operator == 'isNotEmpty':
                        query = query.filter(column.isnot(None) & (column != ''))
                    continue

                if isinstance(column_type, Boolean):
                    if operator == "equals" or operator == "is":
                        query = query.filter(column == value)
                    elif operator == "notEquals":
                        query = query.filter(column != value)
                else:
                    if operator == "equals":
                        query = query.filter(column == value)
                    elif operator == "notEquals":
                        query = query.filter(column != value)
                    elif operator == "contains":
                        if hasattr(column, 'ilike'):
                            query = query.filter(column.ilike(f"%{value}%"))
                        else:
                            query = query.filter(column.contains(value))
                    elif operator == "notContains":
                        if hasattr(column, 'ilike'):
                            query = query.filter(~column.ilike(f"%{value}%"))
                        else:
                            query = query.filter(~column.contains(value))
                    elif operator == "startsWith":
                        if hasattr(column, 'ilike'):
                            query = query.filter(column.ilike(f"{value}%"))
                        else:
                            query = query.filter(column.startswith(value))
                    elif operator == "endsWith":
                        if hasattr(column, 'ilike'):
                            query = query.filter(column.ilike(f"%{value}"))
                        else:
                            query = query.filter(column.endswith(value))

        if sort_by:
            sort_column = getattr(SourceWebsiteModel, sort_by, None)
            if sort_column:
                if sort_order == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())

        total_count = query.count()
        db_source_websites = query.offset(offset).limit(limit).all()

        return (
            [
                SourceWebsiteEntity.SourceWebsite(**db_sw.__dict__)
                for db_sw in db_source_websites
            ],
            total_count,
        )

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
