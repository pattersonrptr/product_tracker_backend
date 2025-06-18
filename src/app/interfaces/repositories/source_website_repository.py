from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Dict, Any

from src.app.entities.source_website import SourceWebsite


class SourceWebsiteRepositoryInterface(ABC):
    @abstractmethod
    def create(self, source_website: SourceWebsite) -> SourceWebsite:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, source_website_id: int) -> Optional[SourceWebsite]:
        raise NotImplementedError

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[SourceWebsite]:
        raise NotImplementedError

    @abstractmethod
    def get_all(
        self,
        column_filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> Tuple[List[SourceWebsite], int]:
        raise NotImplementedError

    @abstractmethod
    def update(
        self, source_website_id: int, source_website: SourceWebsite
    ) -> Optional[SourceWebsite]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, source_website_id: int) -> bool:
        raise NotImplementedError
