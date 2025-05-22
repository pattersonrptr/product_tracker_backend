from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session  # noqa: F401

from src.app.entities import (
    search_config as SearchConfigEntity,
    source_website as SourceWebsiteEntity,
)
from src.app.interfaces.repositories.search_config_repository import (
    SearchConfigRepositoryInterface,
)
from src.app.interfaces.repositories.user_repository import UserRepositoryInterface


class CreateSearchConfigUseCase:
    def __init__(self, search_config_repo: SearchConfigRepositoryInterface, user_repo: UserRepositoryInterface):
        self.search_config_repo = search_config_repo
        self.user_repo = user_repo

    def execute(self, search_config: SearchConfigEntity.SearchConfig) -> SearchConfigEntity.SearchConfig:
        if search_config.user_id and not self.user_repo.get_by_id(search_config.user_id):
            raise ValueError(f"User with id {search_config.user_id} not found")
        return self.search_config_repo.create(search_config)


class GetSearchConfigUseCase:
    def __init__(self, search_config_repo: SearchConfigRepositoryInterface):
        self.search_config_repo = search_config_repo

    def execute(self, search_config_id: int) -> Optional[SearchConfigEntity.SearchConfig]:
        return self.search_config_repo.get_by_id(search_config_id)


class ListSearchConfigsUseCase:
    def __init__(
            self,
            search_config_repo: SearchConfigRepositoryInterface
        ):
        self.search_config_repo = search_config_repo

    def execute(
        self,
        filter_data:  Dict[str, Any],
        limit: int,
        offset: int,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ):
        column_filters = filter_data.get("column_filters", {})

        return self.search_config_repo.get_all(
            column_filters=column_filters,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )


class UpdateSearchConfigUseCase:
    def __init__(self, search_config_repo: SearchConfigRepositoryInterface, user_repo: UserRepositoryInterface):
        self.search_config_repo = search_config_repo
        self.user_repo = user_repo

    def execute(self, search_config_id: int, search_config: SearchConfigEntity.SearchConfig) -> Optional[SearchConfigEntity.SearchConfig]:
        existing_config = self.search_config_repo.get_by_id(search_config_id)
        if not existing_config:
            return None
        if search_config.user_id and not self.user_repo.get_by_id(search_config.user_id):
            raise ValueError(f"User with id {search_config.user_id} not found")
        search_config.id = search_config_id
        return self.search_config_repo.update(search_config_id, search_config)


class DeleteSearchConfigUseCase:
    def __init__(self, search_config_repo: SearchConfigRepositoryInterface):
        self.search_config_repo = search_config_repo

    def execute(self, search_config_id: int) -> bool:
        return self.search_config_repo.delete(search_config_id)


class GetSearchConfigsByUserUseCase:
    def __init__(self, search_config_repo: SearchConfigRepositoryInterface, user_repo: UserRepositoryInterface):
        self.search_config_repo = search_config_repo
        self.user_repo = user_repo

    def execute(self, user_id: int) -> List[SearchConfigEntity.SearchConfig]:
        if not self.user_repo.get_by_id(user_id):
            raise ValueError(f"User with id {user_id} not found")
        return self.search_config_repo.get_by_user_id(user_id)


class GetSearchConfigsBySourceWebsiteUseCase:
    def __init__(self, search_config_repo: SearchConfigRepositoryInterface):
        self.search_config_repo = search_config_repo

    def execute(self, source_website: SourceWebsiteEntity.SourceWebsite) -> List[SearchConfigEntity.SearchConfig]:
        if not source_website.id:
            raise ValueError("SourceWebsite must have an ID to search by.")
        return self.search_config_repo.get_by_source_website(source_website)
