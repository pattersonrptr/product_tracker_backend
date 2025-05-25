from typing import Optional, List, Dict, Any

from sqlalchemy import inspect
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.sqltypes import Boolean

from src.app.infrastructure.database.models.search_config_model import (
    SearchConfig as SearchConfigModel,
)
from src.app.entities import (
    search_config as SearchConfigEntity,
    source_website as SourceWebsiteEntity,
)
from src.app.infrastructure.database.models.source_website_model import (
    SourceWebsite as SourceWebsiteModel,
)
from src.app.interfaces.repositories.search_config_repository import (
    SearchConfigRepositoryInterface,
)


class SearchConfigRepository(SearchConfigRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def create(
        self, search_config: SearchConfigEntity.SearchConfig
    ) -> SearchConfigEntity.SearchConfig:
        try:
            search_config_data = {
                k: v
                for k, v in search_config.model_dump().items()
                if k != "source_websites"
            }
            db_search_config = SearchConfigModel(**search_config_data)

            if search_config.source_websites:
                db_source_websites = []
                for sw_entity in search_config.source_websites:
                    db_sw = (
                        self.db.query(SourceWebsiteModel)
                        .filter(SourceWebsiteModel.id == sw_entity.id)
                        .first()
                    )
                    if db_sw:
                        db_source_websites.append(db_sw)
                db_search_config.source_websites.extend(db_source_websites)

            self.db.add(db_search_config)
            self.db.commit()
            self.db.refresh(db_search_config)
            return SearchConfigEntity.SearchConfig(**db_search_config.__dict__)
        except Exception as e:
            self.db.rollback()
            raise e

    def get_by_id(
        self, search_config_id: int
    ) -> Optional[SearchConfigEntity.SearchConfig]:
        db_search_config = (
            self.db.query(SearchConfigModel)
            .options(joinedload(SearchConfigModel.source_websites))
            .options(joinedload(SearchConfigModel.user))
            .options(joinedload(SearchConfigModel.search_execution_logs))
            .filter(SearchConfigModel.id == search_config_id)
            .first()
        )
        if db_search_config:
            source_websites_entities = [
                SourceWebsiteEntity.SourceWebsite(**sw.__dict__)
                for sw in db_search_config.source_websites
            ]
            return SearchConfigEntity.SearchConfig(
                **{
                    k: v
                    for k, v in db_search_config.__dict__.items()
                    if k not in ["_sa_instance_state", "source_websites"]
                },
                source_websites=source_websites_entities,
            )
        return None

    def get_all(
        self,
        column_filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ):
        query = (
            self.db.query(SearchConfigModel)
            .options(joinedload(SearchConfigModel.source_websites))
            .options(joinedload(SearchConfigModel.user))
            .options(joinedload(SearchConfigModel.search_execution_logs))
        )

        if column_filters:
            for field, filter_info in column_filters.items():
                value = filter_info.get("value")
                operator = filter_info.get("operator", "equals")
                column = getattr(SearchConfigModel, field, None)

                if column is None:
                    print(
                        f"Warning: Filter field '{field}' not found on SearchConfigModel."
                    )
                    continue

                column_type = (
                    inspect(column).type if hasattr(inspect(column), "type") else None
                )

                if value is None:
                    if operator == "isEmpty":
                        query = query.filter(column.is_(None) | (column == ""))
                    elif operator == "isNotEmpty":
                        query = query.filter(column.isnot(None) & (column != ""))
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
                        if hasattr(column, "ilike"):
                            print(column, operator)
                            query = query.filter(column.ilike(f"%{value}%"))
                        else:
                            query = query.filter(column.contains(value))
                    elif operator == "notContains":
                        if hasattr(column, "ilike"):
                            query = query.filter(~column.ilike(f"%{value}%"))
                        else:
                            query = query.filter(~column.contains(value))
                    elif operator == "startsWith":
                        if hasattr(column, "ilike"):
                            query = query.filter(column.ilike(f"{value}%"))
                        else:
                            query = query.filter(column.startswith(value))
                    elif operator == "endsWith":
                        if hasattr(column, "ilike"):
                            query = query.filter(column.ilike(f"%{value}"))
                        else:
                            query = query.filter(column.endswith(value))

        total_count = query.count()

        if sort_by:
            column = getattr(SearchConfigModel, sort_by, None)
            if column is not None:
                if sort_order == "desc":
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())

        query = query.offset(offset).limit(limit)

        db_search_configs = query.all()
        search_configs = []

        for db_sc in db_search_configs:
            source_websites_entities = [
                SourceWebsiteEntity.SourceWebsite(**sw.__dict__)
                for sw in db_sc.source_websites
            ]
            search_config_entity = SearchConfigEntity.SearchConfig(
                **{
                    k: v
                    for k, v in db_sc.__dict__.items()
                    if k not in ["_sa_instance_state", "source_websites"]
                },
                source_websites=source_websites_entities,
            )
            search_configs.append(search_config_entity)
        return search_configs, total_count

    def update(
        self, search_config_id: int, search_config: SearchConfigEntity.SearchConfig
    ) -> Optional[SearchConfigEntity.SearchConfig]:
        db_search_config = (
            self.db.query(SearchConfigModel)
            .filter(SearchConfigModel.id == search_config_id)
            .first()
        )
        if not db_search_config:
            return None
        try:
            for key, value in search_config.model_dump().items():
                if key not in [
                    "id",
                    "user",
                    "search_execution_logs",
                    "source_websites",
                ]:
                    setattr(db_search_config, key, value)

            db_search_config.source_websites.clear()
            if search_config.source_websites:
                for sw_entity in search_config.source_websites:
                    db_sw = (
                        self.db.query(SourceWebsiteModel)
                        .filter(SourceWebsiteModel.id == sw_entity.id)
                        .first()
                    )
                    if db_sw:
                        db_search_config.source_websites.append(db_sw)

            self.db.commit()
            self.db.refresh(db_search_config)
            return self.get_by_id(search_config_id)
        except Exception as e:
            self.db.rollback()
            raise e

    def delete(self, search_config_id: int) -> bool:
        db_search_config = (
            self.db.query(SearchConfigModel)
            .filter(SearchConfigModel.id == search_config_id)
            .first()
        )
        if not db_search_config:
            return False
        try:
            self.db.delete(db_search_config)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e

    def get_by_user_id(self, user_id: int) -> List[SearchConfigEntity.SearchConfig]:
        db_search_configs = (
            self.db.query(SearchConfigModel)
            .options(joinedload(SearchConfigModel.source_websites))
            .options(joinedload(SearchConfigModel.user))
            .options(joinedload(SearchConfigModel.search_execution_logs))
            .filter(SearchConfigModel.user_id == user_id)
            .all()
        )
        search_configs = []
        for db_sc in db_search_configs:
            source_websites_entities = [
                SourceWebsiteEntity.SourceWebsite(**sw.__dict__)
                for sw in db_sc.source_websites
            ]
            search_config_entity = SearchConfigEntity.SearchConfig(
                **{
                    k: v
                    for k, v in db_sc.__dict__.items()
                    if k not in ["_sa_instance_state", "source_websites"]
                },
                source_websites=source_websites_entities,
            )
            search_configs.append(search_config_entity)
        return search_configs

    def get_by_source_website(
        self, source_website: SourceWebsiteEntity.SourceWebsite
    ) -> List[SearchConfigEntity.SearchConfig]:
        db_search_configs = (
            self.db.query(SearchConfigModel)
            .join(SearchConfigModel.source_websites)
            .options(joinedload(SearchConfigModel.user))
            .options(joinedload(SearchConfigModel.search_execution_logs))
            .filter(SourceWebsiteModel.id == source_website.id)
            .all()
        )
        search_configs = []
        for db_sc in db_search_configs:
            source_websites_entities = [
                SourceWebsiteEntity.SourceWebsite(**sw.__dict__)
                for sw in db_sc.source_websites
            ]
            search_config_entity = SearchConfigEntity.SearchConfig(
                **{
                    k: v
                    for k, v in db_sc.__dict__.items()
                    if k not in ["_sa_instance_state", "source_websites"]
                },
                source_websites=source_websites_entities,
            )
            search_configs.append(search_config_entity)
        return search_configs
