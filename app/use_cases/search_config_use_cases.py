from typing import List, Optional

from sqlalchemy.orm import Session  # noqa: F401

from app.entities.search import search_config as SearchConfigEntity
from app.entities.product import source_website as SourceWebsiteEntity
from app.interfaces.repositories.search_config_repository import (
    SearchConfigRepositoryInterface,
)
from app.interfaces.repositories.user_repository import UserRepositoryInterface


class SearchConfigUseCases:
    def __init__(
        self,
        search_config_repo: SearchConfigRepositoryInterface,
        user_repo: UserRepositoryInterface,
    ):
        self.search_config_repo = search_config_repo
        self.user_repo = user_repo

    def create_search_config(
        self, search_config: SearchConfigEntity.SearchConfig
    ) -> SearchConfigEntity.SearchConfig:
        if search_config.user_id and not self.user_repo.get_by_id(
            search_config.user_id
        ):
            raise ValueError(f"User with id {search_config.user_id} not found")
        return self.search_config_repo.create(search_config)

    def get_search_config(
        self, search_config_id: int
    ) -> Optional[SearchConfigEntity.SearchConfig]:
        return self.search_config_repo.get_by_id(search_config_id)

    def get_all_search_configs(self) -> List[SearchConfigEntity.SearchConfig]:
        return self.search_config_repo.get_all()

    def update_search_config(
        self, search_config_id: int, search_config: SearchConfigEntity.SearchConfig
    ) -> Optional[SearchConfigEntity.SearchConfig]:
        existing_config = self.search_config_repo.get_by_id(search_config_id)
        if not existing_config:
            return None
        if search_config.user_id and not self.user_repo.get_by_id(
            search_config.user_id
        ):
            raise ValueError(f"User with id {search_config.user_id} not found")
        search_config.id = search_config_id
        return self.search_config_repo.update(search_config_id, search_config)

    def delete_search_config(self, search_config_id: int) -> bool:
        return self.search_config_repo.delete(search_config_id)

    def get_search_configs_by_user(
        self, user_id: int
    ) -> List[SearchConfigEntity.SearchConfig]:
        if not self.user_repo.get_by_id(user_id):
            raise ValueError(f"User with id {user_id} not found")
        return self.search_config_repo.get_by_user_id(user_id)

    def get_search_configs_by_source_website(
        self, source_website: SourceWebsiteEntity.SourceWebsite
    ) -> List[SearchConfigEntity.SearchConfig]:
        if not source_website.id:
            raise ValueError("SourceWebsite must have an ID to search by.")
        return self.search_config_repo.get_by_source_website(source_website)
