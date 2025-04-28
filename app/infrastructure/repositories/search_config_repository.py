from typing import Optional, List

from sqlalchemy.orm import Session, joinedload

from app.infrastructure.database.models.search_config_model import (
    SearchConfig as SearchConfigModel,
)
from app.entities.search import search_config as SearchConfigEntity
from app.entities.product import source_website as SourceWebsiteEntity
from app.infrastructure.database.models.source_website_model import (
    SourceWebsite as SourceWebsiteModel,
)
from app.interfaces.repositories.search_config_repository import (
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

    def get_all(self) -> List[SearchConfigEntity.SearchConfig]:
        db_search_configs = (
            self.db.query(SearchConfigModel)
            .options(joinedload(SearchConfigModel.source_websites))
            .options(joinedload(SearchConfigModel.user))
            .options(joinedload(SearchConfigModel.search_execution_logs))
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
