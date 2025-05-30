from typing import Optional, List, Dict, Any, Tuple
from abc import ABC, abstractmethod

from src.app.entities import (
    search_config as SearchConfigEntity,
    source_website as SourceWebsiteEntity,
)


class SearchConfigRepositoryInterface(ABC):
    @abstractmethod
    def create(
        self, search_config: SearchConfigEntity.SearchConfig
    ) -> SearchConfigEntity.SearchConfig:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(
        self, search_config_id: int
    ) -> Optional[SearchConfigEntity.SearchConfig]:
        raise NotImplementedError

    @abstractmethod
    def get_all(
        self,
        column_filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> Tuple[List[SearchConfigEntity.SearchConfig], int]:
        raise NotImplementedError

    @abstractmethod
    def update(
        self, search_config_id: int, search_config: SearchConfigEntity.SearchConfig
    ) -> Optional[SearchConfigEntity.SearchConfig]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, search_config_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> List[SearchConfigEntity.SearchConfig]:
        raise NotImplementedError

    @abstractmethod
    def get_by_source_website(
        self, source_website: SourceWebsiteEntity.SourceWebsite
    ) -> List[SearchConfigEntity.SearchConfig]:
        raise NotImplementedError
